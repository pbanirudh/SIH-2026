import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  FileText,
  UploadCloud,
  CheckSquare,
  Database,
  AlertTriangle,
  Download,
  Shield,
  Settings,
  Layers,
  MapPin,
  UserCheck
} from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onSelectPage: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onSelectPage }) => {
  const { t } = useTranslation();

  const menuItems = [
    { id: 'dashboard', labelKey: 'nav.dashboard', icon: LayoutDashboard },
    { id: 'documents', labelKey: 'nav.documents', icon: FileText },
    { id: 'upload', labelKey: 'nav.upload', icon: UploadCloud },
    { id: 'verification', labelKey: 'nav.verification', icon: CheckSquare, badgeCount: 3 },
    { id: 'records', labelKey: 'nav.land_records', icon: Database },
    { id: 'validation', labelKey: 'nav.validation', icon: AlertTriangle },
    { id: 'exports', labelKey: 'nav.exports', icon: Download },
    { id: 'audit', labelKey: 'nav.audit', icon: Shield },
    { id: 'settings', labelKey: 'nav.settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between p-4 min-h-[calc(100vh-64px)] shrink-0">
      <div className="flex flex-col gap-6">
        {/* Branding Logo Header */}
        <div className="flex items-center gap-3 px-2 pt-2">
          <div className="w-10 h-10 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-200">
            <Layers className="w-6 h-6" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-base text-slate-900 tracking-tight flex items-center gap-1">
              {t('app.name')} <span className="text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-semibold border border-indigo-200">v1.0</span>
            </span>
            <span className="text-[10px] text-slate-500 font-medium leading-tight">
              {t('app.subtitle')}
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex flex-col gap-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectPage(item.id)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 border border-indigo-200/60'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                  <span>{t(item.labelKey)}</span>
                </div>
                {item.badgeCount && (
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                    {item.badgeCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Role Card & System Status */}
      <div className="flex flex-col gap-3 pt-4 border-t border-slate-200">
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center">
            <UserCheck className="w-4 h-4 text-slate-600" />
          </div>
          <div className="flex flex-col text-xs">
            <span className="font-bold text-slate-900">{t('nav.user_role')}</span>
            <span className="text-[10px] text-slate-500">Department of Revenue</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
