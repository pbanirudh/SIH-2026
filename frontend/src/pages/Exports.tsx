import React from 'react';
import { Download, FileSpreadsheet, CheckCircle2, AlertTriangle, Layers, Globe } from 'lucide-react';
import { api } from '../services/api';

export const ExportsPage: React.FC = () => {
  const exportCards = [
    {
      title: 'Export Verified Records CSV',
      description: 'Exports only land records that have passed officer human verification.',
      icon: CheckCircle2,
      color: '#10b981',
      url: api.getExportVerifiedCsvUrl(),
      filename: 'land_records_verified.csv',
      tag: 'Recommended for Production'
    },
    {
      title: 'Export All Records CSV',
      description: 'Exports all extracted land records, including unverified and low-confidence items.',
      icon: FileSpreadsheet,
      color: '#3b82f6',
      url: api.getExportAllCsvUrl(),
      filename: 'land_records_all.csv',
      tag: 'Full Database Dump'
    },
    {
      title: 'Export Validation Errors CSV',
      description: 'Exports records that failed format or logical validation for audit review.',
      icon: AlertTriangle,
      color: '#ef4444',
      url: api.getExportErrorsCsvUrl(),
      filename: 'land_records_validation_errors.csv',
      tag: 'Audit & Compliance'
    },
    {
      title: 'Export Raw OCR Bounding Boxes CSV',
      description: 'Exports page-level OCR text, confidence scores, and bounding box coordinates.',
      icon: Layers,
      color: '#8b5cf6',
      url: api.getExportOcrCsvUrl(),
      filename: 'land_records_raw_ocr.csv',
      tag: 'Developer / AI Bounding Box Data'
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>CSV Data Export Portal</h2>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Download structured land record datasets formatted with UTF-8 BOM for Microsoft Excel Indian language rendering.
        </p>
      </div>

      {/* UTF-8 BOM Notice */}
      <div style={{
        background: 'rgba(56, 189, 248, 0.1)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        borderRadius: '10px',
        padding: '14px 18px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <Globe size={20} color="#38bdf8" />
        <div>
          <span style={{ fontSize: '0.88rem', fontWeight: 600, color: '#38bdf8' }}>
            UTF-8 Byte Order Mark (BOM) Encoding Active
          </span>
          <p style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '2px' }}>
            All CSV exports are encoded using <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }}>utf-8-sig</code>. Indian scripts (Hindi, Tamil, Telugu, Marathi, Kannada, Bengali) will open natively in Microsoft Excel, Numbers, and Google Sheets without encoding glitches.
          </p>
        </div>
      </div>

      {/* Export Options Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {exportCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '10px',
                    background: `${card.color}20`,
                    border: `1px solid ${card.color}40`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: card.color
                  }}>
                    <Icon size={22} />
                  </div>
                  <span style={{ fontSize: '0.72rem', padding: '3px 8px', borderRadius: '10px', background: 'rgba(255,255,255,0.06)', color: '#94a3b8', fontWeight: 600 }}>
                    {card.tag}
                  </span>
                </div>

                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#f8fafc' }}>
                  {card.title}
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '6px', lineHeight: 1.5 }}>
                  {card.description}
                </p>
              </div>

              <a
                href={card.url}
                download={card.filename}
                style={{
                  marginTop: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  background: card.color,
                  color: '#fff',
                  padding: '10px',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  fontWeight: 600,
                  fontSize: '0.88rem',
                  boxShadow: `0 4px 12px ${card.color}40`
                }}
              >
                <Download size={16} />
                <span>Download CSV</span>
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
};
