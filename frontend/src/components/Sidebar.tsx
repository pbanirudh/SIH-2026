import React from 'react';
import { LayoutDashboard, UploadCloud, FileText, CheckSquare, Database, AlertTriangle, Download, Shield, Settings } from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onSelectPage: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onSelectPage }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Documents', icon: UploadCloud },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'verification', label: 'Human Verification', icon: CheckSquare },
    { id: 'records', label: 'Land Records', icon: Database },
    { id: 'validation', label: 'Validation Errors', icon: AlertTriangle },
    { id: 'exports', label: 'CSV Exports', icon: Download },
    { id: 'audit', label: 'Audit Logs', icon: Shield },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside style={{
      width: '240px',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderRight: '1px solid rgba(255, 255, 255, 0.1)',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px 12px',
      gap: '4px',
      minHeight: 'calc(100vh - 64px)'
    }}>
      {menuItems.map((item) => {
        const Icon = item.icon;
        const isActive = currentPage === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectPage(item.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '10px 14px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: isActive ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
              color: isActive ? '#60a5fa' : '#94a3b8',
              fontWeight: isActive ? 600 : 400,
              fontSize: '0.88rem',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            }}
            onMouseLeave={(e) => {
              if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <Icon size={18} color={isActive ? '#60a5fa' : '#64748b'} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </aside>
  );
};
