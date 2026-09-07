import React, { useState } from 'react';
import { Sliders, Save, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [highConf, setHighConf] = useState<number>(0.90);
  const [medConf, setMedConf] = useState<number>(0.70);
  const [maxFileSize, setMaxFileSize] = useState<number>(25);
  const [defaultLang, setDefaultLang] = useState<string>('en');
  const [isSaved, setIsSaved] = useState<boolean>(false);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '800px' }}>
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>System Configuration & AI Settings</h2>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Tune PaddleOCR, confidence scoring thresholds, and upload restrictions.
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '12px' }}>
            Confidence Scoring Thresholds
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>HIGH Confidence Cutoff (&gt;=):</label>
              <input
                type="number"
                step="0.05"
                min="0.5"
                max="1.0"
                value={highConf}
                onChange={(e) => setHighConf(parseFloat(e.target.value))}
                style={{
                  width: '100%',
                  marginTop: '6px',
                  background: '#1e293b',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#f8fafc',
                  padding: '8px 12px',
                  borderRadius: '6px'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>MEDIUM Confidence Cutoff (&gt;=):</label>
              <input
                type="number"
                step="0.05"
                min="0.3"
                max="0.9"
                value={medConf}
                onChange={(e) => setMedConf(parseFloat(e.target.value))}
                style={{
                  width: '100%',
                  marginTop: '6px',
                  background: '#1e293b',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#f8fafc',
                  padding: '8px 12px',
                  borderRadius: '6px'
                }}
              />
            </div>
          </div>
        </div>

        <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '16px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '12px' }}>
            Upload Limits & Default OCR Language
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>Max File Upload Size (MB):</label>
              <input
                type="number"
                value={maxFileSize}
                onChange={(e) => setMaxFileSize(parseInt(e.target.value))}
                style={{
                  width: '100%',
                  marginTop: '6px',
                  background: '#1e293b',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#f8fafc',
                  padding: '8px 12px',
                  borderRadius: '6px'
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>Default Document Language:</label>
              <select
                value={defaultLang}
                onChange={(e) => setDefaultLang(e.target.value)}
                style={{
                  width: '100%',
                  marginTop: '6px',
                  background: '#1e293b',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#f8fafc',
                  padding: '8px 12px',
                  borderRadius: '6px'
                }}
              >
                <option value="en">English</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="ta">Tamil (தமிழ்)</option>
                <option value="te">Telugu (తెలుగు)</option>
                <option value="mr">Marathi (मराठी)</option>
              </select>
            </div>
          </div>
        </div>

        <button
          onClick={handleSave}
          style={{
            marginTop: '10px',
            background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
            color: '#fff',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '6px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            cursor: 'pointer'
          }}
        >
          {isSaved ? <Check size={16} /> : <Save size={16} />}
          <span>{isSaved ? 'Settings Saved!' : 'Save Configurations'}</span>
        </button>
      </div>
    </div>
  );
};
