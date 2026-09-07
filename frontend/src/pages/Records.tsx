import React, { useEffect, useState } from 'react';
import { Search, Filter, RefreshCw, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { ExtractedRecord } from '../types';

export const RecordsPage: React.FC = () => {
  const [records, setRecords] = useState<ExtractedRecord[]>([]);
  const [search, setSearch] = useState<string>('');
  const [verificationFilter, setVerificationFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadRecords();
  }, [search, verificationFilter]);

  const loadRecords = async () => {
    setIsLoading(true);
    try {
      const data = await api.getRecords(search, verificationFilter || undefined);
      setRecords(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Structured Land Records</h2>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Query, inspect, and filter extracted land record entities.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <select
            value={verificationFilter}
            onChange={(e) => setVerificationFilter(e.target.value)}
            style={{
              background: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              color: '#f8fafc',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '0.85rem'
            }}
          >
            <option value="">All Verification Statuses</option>
            <option value="VERIFIED">Verified</option>
            <option value="UNVERIFIED">Unverified</option>
            <option value="REJECTED">Rejected</option>
          </select>

          <div style={{ position: 'relative' }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '10px' }} />
            <input
              type="text"
              placeholder="Search owner, survey, khasra..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                background: '#1e293b',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#f8fafc',
                padding: '8px 12px 8px 36px',
                borderRadius: '6px',
                fontSize: '0.85rem'
              }}
            />
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ overflowX: 'auto' }}>
        <table>
          <thead>
            <tr>
              <th>Owner Name</th>
              <th>Survey / Khasra No</th>
              <th>State</th>
              <th>District</th>
              <th>Tehsil</th>
              <th>Village</th>
              <th>Area</th>
              <th>Extraction Conf</th>
              <th>Validation</th>
              <th>Verification</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 ? (
              <tr>
                <td colSpan={10} style={{ textAlign: 'center', color: '#94a3b8', padding: '30px' }}>
                  No land records found matching search filter.
                </td>
              </tr>
            ) : (
              records.map((r) => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 600 }}>{r.owner_name || 'N/A'}</td>
                  <td>{r.survey_number || r.khasra_number || 'N/A'}</td>
                  <td>{r.state || 'N/A'}</td>
                  <td>{r.district || 'N/A'}</td>
                  <td>{r.tehsil || 'N/A'}</td>
                  <td>{r.village || 'N/A'}</td>
                  <td>{r.area ? `${r.area} ${r.area_unit || 'ha'}` : 'N/A'}</td>
                  <td>{((r.extraction_confidence || 0) * 100).toFixed(0)}%</td>
                  <td>
                    <span className={`badge-${r.validation_status.toLowerCase()}`} style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '0.75rem', fontWeight: 600 }}>
                      {r.validation_status}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      background: r.verification_status === 'VERIFIED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: r.verification_status === 'VERIFIED' ? '#34d399' : '#fbbf24'
                    }}>
                      {r.verification_status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
