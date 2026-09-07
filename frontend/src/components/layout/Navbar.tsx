import React from 'react';
import { useTranslation } from 'react-i18next';
import { Search, Bell, Shield, User, ChevronDown } from 'lucide-react';

interface NavbarProps {
  pageTitleKey: string;
}

export const Navbar: React.FC<NavbarProps> = ({ pageTitleKey }) => {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.language || 'en';

  const changeLanguage = (langCode: string) => {
    i18n.changeLanguage(langCode);
    localStorage.setItem('i18nextLng', langCode);
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-40 px-6 flex items-center justify-between shadow-xs">
      {/* Left Page Title */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-slate-900 tracking-tight">
          {t(pageTitleKey)}
        </h1>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-6">
        {/* Global Search Input */}
        <div className="relative hidden md:block">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder={t('common.search')}
            className="w-64 pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-md text-slate-800 placeholder-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Notifications */}
        <button className="relative p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-600 rounded-full" />
        </button>

        {/* Multilingual Language Switcher (English | தமிழ் | हिन्दी) */}
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
          <button
            onClick={() => changeLanguage('en')}
            className={`px-3 py-1 rounded-md transition-all ${
              currentLang.startsWith('en')
                ? 'bg-indigo-600 color-white text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
            }`}
          >
            English
          </button>
          <button
            onClick={() => changeLanguage('ta')}
            className={`px-3 py-1 rounded-md transition-all ${
              currentLang.startsWith('ta')
                ? 'bg-indigo-600 color-white text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
            }`}
          >
            தமிழ்
          </button>
          <button
            onClick={() => changeLanguage('hi')}
            className={`px-3 py-1 rounded-md transition-all ${
              currentLang.startsWith('hi')
                ? 'bg-indigo-600 color-white text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
            }`}
          >
            हिन्दी
          </button>
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center border border-indigo-200">
            VO
          </div>
          <div className="hidden lg:flex flex-col">
            <span className="text-xs font-semibold text-slate-900">Officer Sharma</span>
            <span className="text-[10px] text-slate-500">{t('nav.user_role')}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
