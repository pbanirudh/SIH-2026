import React, { useState } from 'react';
import { ShieldCheck, Globe, Bell, ChevronDown, Cpu } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface NavbarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

const PAGE_LABELS: Record<string, string> = {
  dashboard: 'Dashboard',
  upload: 'Upload Documents',
  documents: 'Documents',
  verification: 'Human Verification',
  records: 'Land Records',
  validation: 'Validation Errors',
  exports: 'CSV Exports',
  audit: 'Audit Logs',
  settings: 'Settings',
};

const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'hi', label: 'हिन्दी', flag: '🇮🇳' },
  { code: 'ta', label: 'தமிழ்', flag: '🇮🇳' },
];

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate }) => {
  const { i18n } = useTranslation();
  const [langOpen, setLangOpen] = useState(false);
  const currentLang = LANGUAGES.find((l) => l.code === i18n.language) || LANGUAGES[0];

  const switchLanguage = (code: string) => {
    i18n.changeLanguage(code);
    setLangOpen(false);
  };

  return (
    <header
      style={{
        height: '62px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.07)',
        backgroundColor: 'rgba(8, 13, 26, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 28px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Left: Logo + Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.45)',
              flexShrink: 0,
            }}
          >
            <ShieldCheck size={20} color="#fff" />
          </div>
          <div>
            <div
              style={{
                fontSize: '0.95rem',
                fontWeight: 800,
                fontFamily: "'Plus Jakarta Sans', sans-serif",
                background: 'linear-gradient(135deg, #a5b4fc, #e0e7ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.2,
              }}
            >
              Bhoomi AI
            </div>
            <div style={{ fontSize: '0.62rem', color: '#475569', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              Land Record Portal
            </div>
          </div>
        </div>

        {/* Separator */}
        <div style={{ width: '1px', height: '24px', background: 'rgba(255,255,255,0.08)' }} />

        {/* Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem' }}>
          <span style={{ color: '#475569' }}>Pages</span>
          <span style={{ color: '#334155' }}>/</span>
          <span style={{ color: '#a5b4fc', fontWeight: 600 }}>{PAGE_LABELS[currentPage] || 'Dashboard'}</span>
        </div>
      </div>

      {/* Right: Status + Lang + User */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Pipeline Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            padding: '5px 12px',
            borderRadius: '20px',
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.18)',
          }}
        >
          <div className="live-dot" />
          <span style={{ fontSize: '0.72rem', color: '#6ee7b7', fontWeight: 600, letterSpacing: '0.01em' }}>
            PaddleOCR Online
          </span>
        </div>

        {/* Language Switcher */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setLangOpen((o) => !o)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 10px',
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '8px',
              color: '#94a3b8',
              fontSize: '0.78rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <Globe size={14} />
            <span>{currentLang.flag} {currentLang.label}</span>
            <ChevronDown size={12} style={{ opacity: 0.6, transform: langOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
          </button>

          {langOpen && (
            <div
              style={{
                position: 'absolute',
                top: 'calc(100% + 6px)',
                right: 0,
                background: '#0e1628',
                border: '1px solid rgba(99,102,241,0.2)',
                borderRadius: '10px',
                overflow: 'hidden',
                zIndex: 100,
                boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
                minWidth: '140px',
                animation: 'scaleIn 0.15s ease both',
              }}
            >
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => switchLanguage(lang.code)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    width: '100%',
                    padding: '9px 14px',
                    background: i18n.language === lang.code ? 'rgba(99,102,241,0.15)' : 'transparent',
                    border: 'none',
                    color: i18n.language === lang.code ? '#a5b4fc' : '#94a3b8',
                    fontSize: '0.82rem',
                    fontWeight: i18n.language === lang.code ? 600 : 400,
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'background 0.15s',
                  }}
                >
                  <span>{lang.flag}</span>
                  <span>{lang.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Notifications */}
        <button
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '8px',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            color: '#64748b',
            position: 'relative',
            transition: 'all 0.2s ease',
          }}
        >
          <Bell size={16} />
          <span
            style={{
              position: 'absolute',
              top: '6px',
              right: '6px',
              width: '6px',
              height: '6px',
              background: '#f43f5e',
              borderRadius: '50%',
              boxShadow: '0 0 6px rgba(244,63,94,0.7)',
            }}
          />
        </button>

        {/* User Avatar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingLeft: '12px', borderLeft: '1px solid rgba(255,255,255,0.07)' }}>
          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '9px',
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              fontSize: '0.8rem',
              color: '#fff',
              letterSpacing: '0.03em',
              boxShadow: '0 2px 8px rgba(99,102,241,0.4)',
            }}
          >
            AD
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#e2e8f0' }}>Admin User</span>
            <span style={{ fontSize: '0.67rem', color: '#475569' }}>Verification Officer</span>
          </div>
        </div>
      </div>
    </header>
  );
};
