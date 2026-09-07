import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, Database, CheckCircle2, AlertTriangle, ArrowUpRight, UploadCloud, Download, Eye } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { api } from '../services/api';
import { DashboardStats, ExtractedRecord } from '../types';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

interface DashboardProps {
  onNavigate: (page: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { t } = useTranslation();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentRecords, setRecentRecords] = useState<ExtractedRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [sData, rData] = await Promise.all([
        api.getDashboardStats(),
        api.getRecords()
      ]);
      setStats(sData);
      setRecentRecords(rData.slice(0, 5));
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !stats) {
    return <div className="text-slate-500 p-6 font-medium text-xs">Loading Dashboard...</div>;
  }

  const stateChartData = Object.entries(stats.state_distribution).map(([key, val]) => ({ name: key, count: val }));
  const confidenceChartData = Object.entries(stats.confidence_distribution).map(([key, val]) => ({ name: key, value: val }));

  return (
    <div className="flex flex-col gap-6">
      {/* Header & Quick Action Buttons */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">{t('dashboard.title')}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{t('dashboard.subtitle')}</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('upload')}
            className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-md shadow-xs transition-all flex items-center gap-1.5"
          >
            <UploadCloud className="w-4 h-4" />
            <span>{t('dashboard.btn_upload_records')}</span>
          </button>
          <button
            onClick={() => onNavigate('verification')}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-md shadow-xs transition-all flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{t('dashboard.btn_review_records')}</span>
          </button>
          <button
            onClick={() => onNavigate('exports')}
            className="px-3.5 py-2 bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-semibold rounded-md shadow-xs transition-all flex items-center gap-1.5"
          >
            <Download className="w-4 h-4 text-indigo-600" />
            <span>{t('dashboard.btn_export_csv')}</span>
          </button>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bhoomi-card p-4 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{t('dashboard.kpi_docs_uploaded')}</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-extrabold text-slate-900">{stats.total_documents}</span>
            <FileText className="w-5 h-5 text-indigo-600" />
          </div>
        </div>

        <div className="bhoomi-card p-4 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{t('dashboard.kpi_records_extracted')}</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-extrabold text-slate-900">{stats.total_records}</span>
            <Database className="w-5 h-5 text-purple-600" />
          </div>
        </div>

        <div className="bhoomi-card p-4 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{t('dashboard.kpi_pending_verification')}</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-extrabold text-amber-600">{stats.records_needing_verification}</span>
            <CheckCircle2 className="w-5 h-5 text-amber-600" />
          </div>
        </div>

        <div className="bhoomi-card p-4 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{t('dashboard.kpi_validation_errors')}</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-extrabold text-rose-600">{stats.validation_errors_count}</span>
            <AlertTriangle className="w-5 h-5 text-rose-600" />
          </div>
        </div>

        <div className="bhoomi-card p-4 flex flex-col justify-between">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{t('dashboard.kpi_verified_records')}</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-extrabold text-emerald-600">{stats.verified_records_count}</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* State-wise Progress Chart */}
        <div className="lg:col-span-7 bhoomi-card p-5 flex flex-col gap-3">
          <h3 className="text-sm font-bold text-slate-900">{t('dashboard.chart_state_progress')}</h3>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stateChartData}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Confidence Distribution Donut */}
        <div className="lg:col-span-5 bhoomi-card p-5 flex flex-col gap-3">
          <h3 className="text-sm font-bold text-slate-900">{t('dashboard.chart_confidence')}</h3>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={confidenceChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }: any) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                >
                  {confidenceChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Processing Table */}
      <div className="bhoomi-card p-5 flex flex-col gap-4">
        <h3 className="text-sm font-bold text-slate-900">{t('dashboard.recent_table_title')}</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                <th className="py-2.5 px-3">{t('dashboard.col_document')}</th>
                <th className="py-2.5 px-3">{t('dashboard.col_location')}</th>
                <th className="py-2.5 px-3">{t('dashboard.col_language')}</th>
                <th className="py-2.5 px-3 text-right">{t('dashboard.col_records')}</th>
                <th className="py-2.5 px-3 text-right">{t('dashboard.col_confidence')}</th>
                <th className="py-2.5 px-3">{t('dashboard.col_status')}</th>
                <th className="py-2.5 px-3 text-right">{t('dashboard.col_action')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentRecords.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-semibold text-slate-900 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-indigo-600" />
                    <span>{r.document_type || 'Land Extract'}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-600">{r.district || r.state || 'N/A'}</td>
                  <td className="py-2.5 px-3 text-slate-600 uppercase font-semibold">{r.language}</td>
                  <td className="py-2.5 px-3 text-right font-medium">{r.fields.length || 1}</td>
                  <td className="py-2.5 px-3 text-right font-bold text-emerald-700">
                    {((r.extraction_confidence || 0.92) * 100).toFixed(0)}%
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      r.verification_status === 'VERIFIED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {r.verification_status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => onNavigate('verification')}
                      className="px-2.5 py-1 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded font-semibold transition-colors"
                    >
                      {t('dashboard.btn_verify')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
