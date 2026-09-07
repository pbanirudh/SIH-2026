import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';
import { ValidationIssue } from '../types';

export const ValidationErrorsPage: React.FC = () => {
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadValidationIssues();
  }, []);

  const loadValidationIssues = async () => {
    setIsLoading(true);
    try {
      const data = await api.getValidationErrors();
      setIssues(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Validation Engine Errors & Warnings</h2>
        <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Format checks, boundary logic violations, duplicate document alerts, and cross-field anomalies.
        </p>
      </div>

      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <table>
          <thead>
            <tr>
              <th>Validation Type</th>
              <th>Rule Name</th>
              <th>Target Field</th>
              <th>Severity Status</th>
              <th>Error Description / Message</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {issues.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', color: '#94a3b8', padding: '30px' }}>
                  No validation errors or warnings detected across documents.
                </td>
              </tr>
            ) : (
              issues.map((iss) => (
                <tr key={iss.id}>
                  <td style={{ textTransform: 'capitalize', fontWeight: 600 }}>{iss.validation_type}</td>
                  <td>{iss.rule_name}</td>
                  <td>{iss.field_name || 'Record Level'}</td>
                  <td>
                    <span style={{
                      padding: '4px 10px',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      background: iss.status === 'INVALID' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: iss.status === 'INVALID' ? '#f87171' : '#fbbf24'
                    }}>
                      {iss.status}
                    </span>
                  </td>
                  <td style={{ color: '#cbd5e1' }}>{iss.message}</td>
                  <td>{new Date(iss.created_at).toLocaleTimeString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
