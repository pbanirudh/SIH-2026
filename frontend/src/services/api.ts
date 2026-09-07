import { DocumentItem, ProcessingJob, ExtractedRecord, ValidationIssue, DashboardStats, AuditLog } from '../types';
import { MOCK_DOCUMENTS, MOCK_RECORDS, MOCK_DASHBOARD_STATS } from './mockData';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const IS_DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

export const api = {
  isDemoMode: IS_DEMO_MODE,

  // Document Upload & List
  uploadDocuments: async (files: File[], language: string = 'en'): Promise<DocumentItem[]> => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));
      formData.append('expected_language', language);

      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed');
      return await res.json();
    } catch (err) {
      console.warn('Backend unavailable, using Demo Mode upload response');
      return files.map((f, idx) => ({
        id: `demo-doc-${Date.now()}-${idx}`,
        filename: f.name,
        original_filename: f.name,
        file_type: f.name.split('.').pop() || 'pdf',
        file_size: f.size,
        expected_language: language,
        detected_language: language,
        status: 'completed',
        total_pages: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }));
    }
  },

  getDocuments: async (search?: string, status?: string): Promise<DocumentItem[]> => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      
      const res = await fetch(`${API_BASE}/documents?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch documents');
      return await res.json();
    } catch (err) {
      let filtered = [...MOCK_DOCUMENTS];
      if (search) {
        filtered = filtered.filter((d) => d.original_filename.toLowerCase().includes(search.toLowerCase()));
      }
      return filtered;
    }
  },

  getDocumentDetail: async (id: string): Promise<DocumentItem> => {
    try {
      const res = await fetch(`${API_BASE}/documents/${id}`);
      if (!res.ok) throw new Error('Failed to fetch document detail');
      return await res.json();
    } catch (err) {
      return MOCK_DOCUMENTS.find((d) => d.id === id) || MOCK_DOCUMENTS[0];
    }
  },

  getDocumentStatus: async (id: string): Promise<ProcessingJob[]> => {
    try {
      const res = await fetch(`${API_BASE}/documents/${id}/status`);
      if (!res.ok) throw new Error('Failed to fetch processing status');
      return await res.json();
    } catch (err) {
      return [
        { id: 'j-1', stage: 'upload', status: 'completed', progress_pct: 100, started_at: new Date().toISOString() },
        { id: 'j-2', stage: 'preprocessing', status: 'completed', progress_pct: 100, started_at: new Date().toISOString() },
        { id: 'j-3', stage: 'ocr', status: 'completed', progress_pct: 100, started_at: new Date().toISOString() },
        { id: 'j-4', stage: 'nlp', status: 'completed', progress_pct: 100, started_at: new Date().toISOString() },
        { id: 'j-5', stage: 'validation', status: 'completed', progress_pct: 100, started_at: new Date().toISOString() }
      ];
    }
  },

  // Records & Verification
  getRecords: async (search?: string, verification_status?: string, validation_status?: string): Promise<ExtractedRecord[]> => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (verification_status) params.append('verification_status', verification_status);
      if (validation_status) params.append('validation_status', validation_status);

      const res = await fetch(`${API_BASE}/records?${params.toString()}`);
      if (!res.ok) throw new Error('Failed to fetch land records');
      return await res.json();
    } catch (err) {
      let filtered = [...MOCK_RECORDS];
      if (verification_status) {
        filtered = filtered.filter((r) => r.verification_status === verification_status);
      }
      if (search) {
        filtered = filtered.filter((r) =>
          (r.owner_name || '').toLowerCase().includes(search.toLowerCase()) ||
          (r.survey_number || '').toLowerCase().includes(search.toLowerCase())
        );
      }
      return filtered;
    }
  },

  getRecordDetail: async (id: string): Promise<ExtractedRecord> => {
    try {
      const res = await fetch(`${API_BASE}/records/${id}`);
      if (!res.ok) throw new Error('Failed to fetch record detail');
      return await res.json();
    } catch (err) {
      return MOCK_RECORDS.find((r) => r.id === id) || MOCK_RECORDS[0];
    }
  },

  verifyRecord: async (
    id: string,
    fields: { field_name: string; action: string; corrected_value?: string }[],
    verification_status: 'VERIFIED' | 'REJECTED' = 'VERIFIED',
    remarks?: string
  ): Promise<ExtractedRecord> => {
    try {
      const res = await fetch(`${API_BASE}/records/${id}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fields, verification_status, remarks }),
      });
      if (!res.ok) throw new Error('Failed to submit verification');
      return await res.json();
    } catch (err) {
      const rec = MOCK_RECORDS.find((r) => r.id === id) || MOCK_RECORDS[0];
      rec.verification_status = verification_status;
      return rec;
    }
  },

  // Validation Errors
  getValidationErrors: async (): Promise<ValidationIssue[]> => {
    try {
      const res = await fetch(`${API_BASE}/validation/errors`);
      if (!res.ok) throw new Error('Failed to fetch validation errors');
      return await res.json();
    } catch (err) {
      return [
        {
          id: 'val-001',
          field_name: 'survey_number',
          rule_name: 'survey_format_pattern',
          validation_type: 'format',
          status: 'WARNING',
          message: 'Survey Number "124//3A" contains invalid double slash sequence',
          created_at: new Date().toISOString()
        },
        {
          id: 'val-002',
          field_name: 'area',
          rule_name: 'positive_area_boundary',
          validation_type: 'logical',
          status: 'INVALID',
          message: 'Area value "-2.5 acres" is negative, failing land area rules',
          created_at: new Date().toISOString()
        }
      ];
    }
  },

  // Dashboard Stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    try {
      const res = await fetch(`${API_BASE}/dashboard/statistics`);
      if (!res.ok) throw new Error('Failed to fetch dashboard statistics');
      return await res.json();
    } catch (err) {
      return MOCK_DASHBOARD_STATS;
    }
  },

  // Audit Logs
  getAuditLogs: async (): Promise<AuditLog[]> => {
    try {
      const res = await fetch(`${API_BASE}/audit/logs`);
      if (!res.ok) throw new Error('Failed to fetch audit logs');
      return await res.json();
    } catch (err) {
      return [
        {
          id: 'audit-001',
          user_email: 'officer.pune@landrecords.gov.in',
          action: 'verify_record',
          resource_type: 'record',
          resource_id: 'rec-102',
          details_json: { field: 'survey_number', original: '124/3A', verified: '124/3B' },
          timestamp: new Date().toISOString()
        }
      ];
    }
  },

  // Export URLs
  getExportAllCsvUrl: () => `${API_BASE}/export/csv`,
  getExportVerifiedCsvUrl: () => `${API_BASE}/export/verified-csv`,
  getExportErrorsCsvUrl: () => `${API_BASE}/export/errors-csv`,
  getExportOcrCsvUrl: () => `${API_BASE}/export/ocr-csv`,
};
