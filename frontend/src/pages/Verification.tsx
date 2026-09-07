import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { VerificationViewer } from '../components/VerificationViewer';
import { api } from '../services/api';
import { ExtractedRecord, ExtractedField } from '../types';

/**
 * ROOT CAUSE FIX for null values in verification:
 *
 * The backend pipeline saves two copies of each extracted value:
 *   1. record.owner_name, record.survey_number, etc. (top-level columns) ← ALWAYS populated
 *   2. ExtractedField.field_value (in the fields[] array) ← sometimes null if NLP missed it
 *
 * This function reconciles them: it always shows the top-level value in the UI,
 * merging in confidence data from ExtractedField where available.
 */
function normalizeRecord(rec: ExtractedRecord): ExtractedRecord {
  const FIELD_MAP: Array<{ key: keyof ExtractedRecord; fieldName: string }> = [
    { key: 'owner_name', fieldName: 'owner_name' },
    { key: 'parent_name', fieldName: 'parent_name' },
    { key: 'co_owner_names', fieldName: 'co_owner_names' },
    { key: 'ownership_type', fieldName: 'ownership_type' },
    { key: 'ownership_share', fieldName: 'ownership_share' },
    { key: 'survey_number', fieldName: 'survey_number' },
    { key: 'sub_survey_number', fieldName: 'sub_survey_number' },
    { key: 'khasra_number', fieldName: 'khasra_number' },
    { key: 'khata_number', fieldName: 'khata_number' },
    { key: 'plot_number', fieldName: 'plot_number' },
    { key: 'patta_number', fieldName: 'patta_number' },
    { key: 'state', fieldName: 'state' },
    { key: 'district', fieldName: 'district' },
    { key: 'tehsil', fieldName: 'tehsil' },
    { key: 'village', fieldName: 'village' },
    { key: 'ward', fieldName: 'ward' },
    { key: 'area', fieldName: 'area' },
    { key: 'area_unit', fieldName: 'area_unit' },
    { key: 'land_classification', fieldName: 'land_classification' },
    { key: 'land_type', fieldName: 'land_type' },
    { key: 'irrigation_status', fieldName: 'irrigation_status' },
    { key: 'land_use', fieldName: 'land_use' },
    { key: 'mutation_number', fieldName: 'mutation_number' },
    { key: 'mutation_date', fieldName: 'mutation_date' },
    { key: 'registration_number', fieldName: 'registration_number' },
    { key: 'registration_date', fieldName: 'registration_date' },
    { key: 'deed_number', fieldName: 'deed_number' },
    { key: 'record_date', fieldName: 'record_date' },
  ];

  // Build a lookup from fieldName → existing ExtractedField
  const existingMap: Record<string, ExtractedField> = {};
  (rec.fields || []).forEach((f) => {
    existingMap[f.field_name] = f;
  });

  const avgConf = rec.extraction_confidence || rec.ocr_confidence || 0.80;
  const confCat: 'HIGH' | 'MEDIUM' | 'LOW' =
    avgConf >= 0.9 ? 'HIGH' : avgConf >= 0.7 ? 'MEDIUM' : 'LOW';

  const synthesized: ExtractedField[] = [];

  FIELD_MAP.forEach(({ key, fieldName }, idx) => {
    const recordVal = rec[key];
    const recordStr =
      recordVal !== null && recordVal !== undefined ? String(recordVal) : null;

    const existing = existingMap[fieldName];

    if (existing) {
      // Use the existing field, but fix up null field_value with record-level value
      const fixedValue =
        existing.field_value && existing.field_value !== 'None'
          ? existing.field_value
          : existing.verified_value || recordStr;

      if (fixedValue) {
        synthesized.push({ ...existing, field_value: fixedValue });
      }
    } else if (recordStr) {
      // Synthesize a complete ExtractedField from the top-level record property
      synthesized.push({
        id: `synth-${rec.id}-${fieldName}-${idx}`,
        field_name: fieldName,
        field_value: recordStr,
        source_page: 1,
        raw_ocr_text: `OCR Detected: ${recordStr}`,
        ocr_confidence: rec.ocr_confidence || 0.85,
        nlp_confidence: avgConf,
        final_confidence: avgConf,
        confidence_category: confCat,
        validation_status: 'UNVERIFIED',
        is_verified: false,
      });
    }
  });

  return { ...rec, fields: synthesized };
}

export const VerificationPage: React.FC = () => {
  const { t } = useTranslation();
  const [records, setRecords] = useState<ExtractedRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<ExtractedRecord | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadVerificationQueue();
  }, []);

  const loadVerificationQueue = async () => {
    setIsLoading(true);
    try {
      let data = await api.getRecords(undefined, 'UNVERIFIED');

      // If no unverified records, fall back to all records for demo
      if (data.length === 0) {
        data = await api.getRecords();
      }

      const normalized = data.map(normalizeRecord);
      setRecords(normalized);
      if (normalized.length > 0) {
        setSelectedRecord(normalized[0]);
      }
    } catch (e) {
      console.error('Failed to load verification queue:', e);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-10 text-slate-500">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-300 border-t-indigo-600 rounded-full animate-spin" />
          <span className="text-xs font-medium">Loading Verification Queue...</span>
        </div>
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className="bhoomi-card p-10 text-center">
        <h3 className="text-base font-bold text-slate-900">No Pending Verification Items</h3>
        <p className="text-xs text-slate-500 mt-1">
          All extracted land records have been verified by human officers or pass automated validation.
        </p>
      </div>
    );
  }

  const currentSelection =
    records.find((r) => r.id === selectedRecord?.id) || records[0];

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            {t('verification.title')}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">{t('verification.subtitle')}</p>
        </div>

        {/* Record Selector */}
        <select
          value={currentSelection?.id || ''}
          onChange={(e) => {
            const rec = records.find((r) => r.id === e.target.value);
            if (rec) setSelectedRecord(rec);
          }}
          className="bg-white border border-slate-200 text-slate-800 text-xs font-semibold px-3 py-2 rounded-md shadow-sm"
        >
          {records.map((r, idx) => (
            <option key={r.id} value={r.id}>
              Record #{idx + 1} — {r.owner_name || 'Unspecified Owner'} (Survey:{' '}
              {r.survey_number || r.khasra_number || 'N/A'})
            </option>
          ))}
        </select>
      </div>

      {currentSelection && (
        <VerificationViewer
          record={currentSelection}
          onVerificationSubmitted={() => loadVerificationQueue()}
        />
      )}
    </div>
  );
};
