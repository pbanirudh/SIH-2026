import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  CheckCircle2, XCircle, Edit3, AlertTriangle, ShieldCheck,
  Zap, Eye, FileText, MapPin, User, Hash, Layers
} from 'lucide-react';
import { ExtractedRecord, ExtractedField } from '../types';
import { api } from '../services/api';

interface VerificationViewerProps {
  record: ExtractedRecord;
  onVerificationSubmitted: () => void;
}

/** Safely extract a displayable value from a field — never returns "None" */
function getDisplayValue(field: ExtractedField): string | null {
  const candidates = [
    field.verified_value,
    field.field_value,
  ];
  for (const c of candidates) {
    if (c && c !== 'None' && c !== 'null' && c.trim() !== '') return c;
  }
  return null;
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const cls =
    pct >= 90
      ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
      : pct >= 70
      ? 'bg-amber-100 text-amber-800 border border-amber-200'
      : 'bg-rose-100 text-rose-800 border border-rose-200';
  return (
    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${cls}`}>
      {pct}%
    </span>
  );
}

const FIELD_GROUPS: { title: string; icon: React.ReactNode; keys: string[] }[] = [
  {
    title: 'Owner & Ownership',
    icon: <User className="w-3.5 h-3.5" />,
    keys: ['owner_name', 'co_owner_names', 'parent_name', 'ownership_type', 'ownership_share'],
  },
  {
    title: 'Land Identification',
    icon: <Hash className="w-3.5 h-3.5" />,
    keys: ['survey_number', 'sub_survey_number', 'khasra_number', 'khata_number', 'plot_number', 'patta_number'],
  },
  {
    title: 'Location',
    icon: <MapPin className="w-3.5 h-3.5" />,
    keys: ['state', 'district', 'tehsil', 'village', 'ward'],
  },
  {
    title: 'Land Details',
    icon: <Layers className="w-3.5 h-3.5" />,
    keys: ['area', 'area_unit', 'land_classification', 'land_type', 'irrigation_status', 'land_use'],
  },
  {
    title: 'Mutation & Registration',
    icon: <FileText className="w-3.5 h-3.5" />,
    keys: ['mutation_number', 'mutation_date', 'registration_number', 'registration_date', 'deed_number', 'record_date'],
  },
];

export const VerificationViewer: React.FC<VerificationViewerProps> = ({
  record,
  onVerificationSubmitted,
}) => {
  const { t } = useTranslation();

  // Pre-fill state with extracted values for 1-click approval
  const [fieldStates, setFieldStates] = useState<
    Record<string, { value: string; isEditing: boolean }>
  >(() => {
    const initial: Record<string, { value: string; isEditing: boolean }> = {};
    record.fields.forEach((f) => {
      initial[f.field_name] = {
        value: getDisplayValue(f) || '',
        isEditing: false,
      };
    });
    return initial;
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [remarks, setRemarks] = useState(record.remarks || '');

  const handleFieldChange = (fieldName: string, newValue: string) => {
    setFieldStates((prev) => ({
      ...prev,
      [fieldName]: { ...prev[fieldName], value: newValue },
    }));
  };

  const toggleEdit = (fieldName: string) => {
    setFieldStates((prev) => ({
      ...prev,
      [fieldName]: { ...prev[fieldName], isEditing: !prev[fieldName].isEditing },
    }));
  };

  const handleBatchApprove = async () => {
    setIsSubmitting(true);
    try {
      const updates = Object.entries(fieldStates).map(([fieldName, state]) => ({
        field_name: fieldName,
        action: 'accept',
        corrected_value: state.value,
      }));
      await api.verifyRecord(
        record.id,
        updates,
        'VERIFIED',
        remarks || '1-Click Batch Approved by Officer'
      );
      onVerificationSubmitted();
    } catch {
      alert('Error submitting verification. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!remarks.trim()) {
      alert('Please provide a reason for rejection in the remarks field.');
      return;
    }
    setIsSubmitting(true);
    try {
      const updates = Object.entries(fieldStates).map(([fieldName, state]) => ({
        field_name: fieldName,
        action: 'reject',
        corrected_value: state.value,
      }));
      await api.verifyRecord(record.id, updates, 'REJECTED', remarks);
      onVerificationSubmitted();
    } catch {
      alert('Error submitting rejection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Build field groups — only show groups that have at least one field
  const fieldByName = Object.fromEntries(record.fields.map((f) => [f.field_name, f]));

  const groups = FIELD_GROUPS.map((group) => ({
    ...group,
    fields: group.keys
      .map((k) => fieldByName[k])
      .filter((f): f is ExtractedField => !!f),
  })).filter((g) => g.fields.length > 0);

  // Also gather any fields not in predefined groups
  const knownKeys = new Set(FIELD_GROUPS.flatMap((g) => g.keys));
  const otherFields = record.fields.filter((f) => !knownKeys.has(f.field_name));
  if (otherFields.length > 0) {
    groups.push({ title: 'Other Fields', icon: <FileText className="w-3.5 h-3.5" />, fields: otherFields });
  }

  const totalFields = record.fields.length;
  const detectedFields = record.fields.filter((f) => getDisplayValue(f)).length;
  const highConfFields = record.fields.filter(
    (f) => f.confidence_category === 'HIGH' && getDisplayValue(f)
  ).length;

  return (
    <div className="flex flex-col gap-4">
      {/* Top Banner: 1-Click Approval */}
      <div className="bg-gradient-to-r from-indigo-800 to-slate-800 text-white rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-300 shrink-0">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold flex items-center gap-2 flex-wrap">
              Rapid 1-Click Verification
              <span className="text-[11px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">
                Pre-filled from OCR
              </span>
            </h2>
            <p className="text-xs text-slate-300 mt-0.5">
              <span className="font-semibold text-white">{detectedFields}</span> of{' '}
              <span className="font-semibold text-white">{totalFields}</span> fields detected · 
              <span className="text-emerald-300 font-semibold"> {highConfFields} high-confidence</span>. 
              Review below and approve or correct.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleReject}
            disabled={isSubmitting}
            className="px-4 py-2 bg-rose-600/80 hover:bg-rose-600 text-white text-xs font-semibold rounded-lg transition-all disabled:opacity-50"
          >
            <XCircle className="w-3.5 h-3.5 inline mr-1.5" />
            {t('verification.btn_reject_record')}
          </button>
          <button
            onClick={handleBatchApprove}
            disabled={isSubmitting}
            className="px-5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold rounded-lg transition-all shadow disabled:opacity-50 flex items-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4" />
            {isSubmitting ? 'Submitting...' : '1-Click Approve All'}
          </button>
        </div>
      </div>

      {/* Main Layout: Document Preview + Extracted Fields */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* LEFT: Original Document */}
        <div className="lg:col-span-5 bhoomi-card p-4 flex flex-col">
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-200">
            <Eye className="w-4 h-4 text-indigo-600" />
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              {t('verification.original_document')}
            </span>
            <span className="ml-auto text-[10px] text-slate-400 font-mono">
              {record.document_id.slice(0, 10)}…
            </span>
          </div>

          <div className="flex-1 bg-slate-900 rounded-lg overflow-auto flex items-center justify-center border border-slate-700 min-h-[400px]">
            <img
              src={`http://localhost:8000/storage/processed/${record.document_id}_page_1.png`}
              onError={(e) => {
                (e.target as HTMLImageElement).src =
                  'https://placehold.co/800x1100/1e293b/f8fafc?text=Land+Record+Document%0APreview+Unavailable';
              }}
              alt="Original Document"
              className="max-w-full h-auto rounded"
            />
          </div>

          {/* Record meta */}
          <div className="mt-3 pt-3 border-t border-slate-200 grid grid-cols-2 gap-2 text-[11px]">
            <div className="flex flex-col">
              <span className="text-slate-400 uppercase tracking-wider font-semibold">Doc Type</span>
              <span className="text-slate-800 font-semibold">{record.document_type || '—'}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-400 uppercase tracking-wider font-semibold">Language</span>
              <span className="text-slate-800 font-semibold">{record.language?.toUpperCase() || '—'}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-400 uppercase tracking-wider font-semibold">OCR Engine</span>
              <span className="text-slate-800 font-semibold">{record.ocr_engine || 'PaddleOCR'}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-400 uppercase tracking-wider font-semibold">OCR Confidence</span>
              <span className="text-slate-800 font-semibold">
                {Math.round((record.ocr_confidence || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>

        {/* RIGHT: Extracted Field Groups */}
        <div className="lg:col-span-7 bhoomi-card p-5 flex flex-col gap-5 overflow-y-auto max-h-[800px]">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-indigo-600" />
                {t('verification.extracted_record')}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                All fields are pre-populated from OCR. Only edit if a correction is needed.
              </p>
            </div>
            <span
              className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                record.validation_status === 'VALID'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : record.validation_status === 'WARNING'
                  ? 'bg-amber-50 text-amber-700 border-amber-200'
                  : 'bg-rose-50 text-rose-700 border-rose-200'
              }`}
            >
              {record.validation_status}
            </span>
          </div>

          {groups.length === 0 && (
            <div className="text-center py-8 text-slate-400">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm font-medium">No fields could be extracted from this document.</p>
              <p className="text-xs mt-1">The OCR engine may not have recognized the document format.</p>
            </div>
          )}

          {groups.map((group, gIdx) => (
            <div key={gIdx} className="flex flex-col gap-2.5">
              <h4 className="flex items-center gap-1.5 text-[11px] font-bold text-indigo-700 uppercase tracking-wider bg-indigo-50 px-2.5 py-1.5 rounded border border-indigo-100 w-fit">
                {group.icon}
                {group.title}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {group.fields.map((field) => {
                  const displayVal = getDisplayValue(field);
                  const state = fieldStates[field.field_name];
                  const editedVal = state?.value ?? displayVal ?? '';

                  return (
                    <div
                      key={field.id}
                      className="p-3 rounded-lg border border-slate-200 bg-white hover:border-indigo-300 transition-colors"
                    >
                      {/* Field label row */}
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[11px] font-semibold text-slate-600 capitalize">
                          {field.field_name.replace(/_/g, ' ')}
                        </span>
                        <div className="flex items-center gap-1">
                          <ConfidenceBadge value={field.final_confidence} />
                          <button
                            type="button"
                            onClick={() => toggleEdit(field.field_name)}
                            className="p-1 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors"
                            title="Edit value"
                          >
                            <Edit3 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>

                      {/* Value display or input */}
                      {state?.isEditing ? (
                        <input
                          type="text"
                          value={editedVal}
                          onChange={(e) => handleFieldChange(field.field_name, e.target.value)}
                          className="w-full text-xs font-semibold text-slate-900 bg-white border border-indigo-500 rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                          autoFocus
                        />
                      ) : (
                        <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 min-h-[30px]">
                          {editedVal ? (
                            <span className="text-xs font-bold text-slate-900">{editedVal}</span>
                          ) : (
                            <span className="text-xs italic text-slate-400 font-normal">Not detected</span>
                          )}
                          {editedVal && (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 ml-1" />
                          )}
                        </div>
                      )}

                      {/* OCR raw text (source context) */}
                      {field.raw_ocr_text && field.raw_ocr_text.trim() && (
                        <p className="mt-1 text-[10px] text-slate-400 truncate" title={field.raw_ocr_text}>
                          OCR: {field.raw_ocr_text}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Bottom action bar */}
          <div className="pt-4 border-t border-slate-200 flex flex-col gap-3 mt-auto">
            <input
              type="text"
              placeholder={t('verification.officer_remarks')}
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded px-3 py-2 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400"
            />
            <div className="flex gap-2">
              <button
                onClick={handleReject}
                disabled={isSubmitting}
                className="flex-1 py-2 bg-white border border-rose-200 hover:bg-rose-50 text-rose-700 font-bold text-xs rounded-lg shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                <XCircle className="w-3.5 h-3.5" />
                {t('verification.btn_reject_record')}
              </button>
              <button
                onClick={handleBatchApprove}
                disabled={isSubmitting}
                className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-lg shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                {isSubmitting ? 'Submitting...' : t('verification.btn_approve_record')}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
