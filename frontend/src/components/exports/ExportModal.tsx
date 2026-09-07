import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Download, CheckSquare, FileSpreadsheet, Loader2 } from 'lucide-react';
import { api } from '../../services/api';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();

  const [scope, setScope] = useState<'verified' | 'all' | 'review' | 'errors'>('verified');
  const [categories, setCategories] = useState({
    owner: true,
    landId: true,
    location: true,
    landDetails: true,
    registration: true,
    confidence: true,
  });

  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [downloadReadyUrl, setDownloadReadyUrl] = useState<string | null>(null);

  if (!isOpen) return null;

  const toggleCategory = (key: keyof typeof categories) => {
    setCategories((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleGenerateCsv = () => {
    setIsExporting(true);
    setDownloadReadyUrl(null);

    setTimeout(() => {
      let exportUrl = api.getExportVerifiedCsvUrl();
      if (scope === 'all') exportUrl = api.getExportAllCsvUrl();
      if (scope === 'errors') exportUrl = api.getExportErrorsCsvUrl();

      setDownloadReadyUrl(exportUrl);
      setIsExporting(false);
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-xl shadow-xl max-w-lg w-full p-6 flex flex-col gap-5 animate-in fade-in zoom-in duration-150">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center gap-2 text-slate-900">
            <FileSpreadsheet className="w-5 h-5 text-indigo-600" />
            <h3 className="text-base font-bold">{t('exports.modal_title')}</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-md">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Record Scope Options */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            {t('exports.modal_record_scope')}
          </label>
          <div className="grid grid-cols-2 gap-2">
            {[
              { id: 'verified', label: t('exports.scope_verified') },
              { id: 'all', label: t('exports.scope_all') },
              { id: 'review', label: t('exports.scope_review') },
              { id: 'errors', label: t('exports.scope_errors') },
            ].map((opt) => (
              <label
                key={opt.id}
                className={`flex items-center gap-2 p-2.5 rounded-lg border text-xs font-medium cursor-pointer transition-all ${
                  scope === opt.id
                    ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-semibold'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                <input
                  type="radio"
                  name="scope"
                  checked={scope === opt.id}
                  onChange={() => setScope(opt.id as any)}
                  className="text-indigo-600 focus:ring-indigo-500"
                />
                <span>{opt.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Field Category Checkboxes */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            {t('exports.modal_select_fields')}
          </label>
          <div className="flex flex-col gap-1.5 bg-slate-50 p-3 rounded-lg border border-slate-200">
            {[
              { key: 'owner', label: t('exports.cat_owner_info') },
              { key: 'landId', label: t('exports.cat_land_id') },
              { key: 'location', label: t('exports.cat_location') },
              { key: 'landDetails', label: t('exports.cat_land_details') },
              { key: 'registration', label: t('exports.cat_registration') },
              { key: 'confidence', label: t('exports.cat_confidence') },
            ].map((cat) => (
              <label key={cat.key} className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={categories[cat.key as keyof typeof categories]}
                  onChange={() => toggleCategory(cat.key as keyof typeof categories)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <span>{cat.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-md"
          >
            Cancel
          </button>

          {downloadReadyUrl ? (
            <a
              href={downloadReadyUrl}
              download="land_records_export.csv"
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-md flex items-center gap-2 shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>Download CSV (UTF-8 BOM)</span>
            </a>
          ) : (
            <button
              onClick={handleGenerateCsv}
              disabled={isExporting}
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-md flex items-center gap-2 shadow-sm disabled:opacity-50"
            >
              {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              <span>{isExporting ? 'Generating...' : t('exports.btn_generate_csv')}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
