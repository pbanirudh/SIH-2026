import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { UploadPage } from './pages/Upload';
import { DocumentsPage } from './pages/Documents';
import { VerificationPage } from './pages/Verification';
import { RecordsPage } from './pages/Records';
import { ValidationErrorsPage } from './pages/ValidationErrors';
import { ExportsPage } from './pages/Exports';
import { AuditLogsPage } from './pages/AuditLogs';
import { SettingsPage } from './pages/Settings';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [pageKey, setPageKey] = useState<number>(0);

  const navigateTo = (page: string) => {
    if (page === currentPage) return;
    setCurrentPage(page);
    setPageKey((k) => k + 1);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':    return <Dashboard onNavigate={navigateTo} />;
      case 'upload':       return <UploadPage />;
      case 'documents':    return <DocumentsPage />;
      case 'verification': return <VerificationPage />;
      case 'records':      return <RecordsPage />;
      case 'validation':   return <ValidationErrorsPage />;
      case 'exports':      return <ExportsPage />;
      case 'audit':        return <AuditLogsPage />;
      case 'settings':     return <SettingsPage />;
      default:             return <Dashboard onNavigate={navigateTo} />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', position: 'relative' }}>
      {/* Animated Background Mesh */}
      <div className="app-bg" />

      {/* Layout */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar currentPage={currentPage} onNavigate={navigateTo} />

        <div style={{ display: 'flex', flex: 1 }}>
          <Sidebar currentPage={currentPage} onSelectPage={navigateTo} />

          {/* Main Content with Page Transition */}
          <main
            key={pageKey}
            className="animate-fade-slide"
            style={{
              flex: 1,
              padding: '28px 32px',
              overflowY: 'auto',
              maxWidth: '1600px',
              width: '100%',
            }}
          >
            {renderPage()}
          </main>
        </div>
      </div>
    </div>
  );
};

export default App;
