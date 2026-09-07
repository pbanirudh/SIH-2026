import { DocumentItem, ExtractedRecord, DashboardStats, ValidationIssue, AuditLog } from '../types';

export const MOCK_DOCUMENTS: DocumentItem[] = [
  {
    id: 'doc-001',
    filename: 'patta_001.pdf',
    original_filename: 'patta_001.pdf',
    file_type: 'pdf',
    file_size: 1420000,
    expected_language: 'ta',
    detected_language: 'ta',
    status: 'completed',
    total_pages: 12,
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 2).toISOString()
  },
  {
    id: 'doc-002',
    filename: 'land_024.pdf',
    original_filename: 'land_024.pdf',
    file_type: 'pdf',
    file_size: 2150000,
    expected_language: 'ta',
    detected_language: 'ta',
    status: 'completed',
    total_pages: 8,
    created_at: new Date(Date.now() - 3600000 * 5).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 5).toISOString()
  },
  {
    id: 'doc-003',
    filename: 'khasra_108.pdf',
    original_filename: 'khasra_108.pdf',
    file_type: 'pdf',
    file_size: 980000,
    expected_language: 'hi',
    detected_language: 'hi',
    status: 'completed',
    total_pages: 14,
    created_at: new Date(Date.now() - 3600000 * 12).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 12).toISOString()
  }
];

export const MOCK_RECORDS: ExtractedRecord[] = [
  {
    id: 'rec-101',
    document_id: 'doc-001',
    document_type: 'Patta / Chitta Passbook',
    state: 'Tamil Nadu',
    district: 'Coimbatore',
    tehsil: 'Pollachi',
    village: 'Anaimalai',
    owner_name: 'Murugan K',
    parent_name: 'Kandasamy',
    survey_number: '123/4A',
    patta_number: '882',
    area: 1.45,
    area_unit: 'hectares',
    land_classification: 'Wet Land (நஞ்சை)',
    language: 'ta',
    ocr_engine: 'PaddleOCR',
    ocr_confidence: 0.96,
    extraction_confidence: 0.94,
    validation_status: 'VALID',
    verification_status: 'VERIFIED',
    fields: [
      { id: 'f-1', field_name: 'owner_name', field_value: 'Murugan K', source_page: 1, raw_ocr_text: 'உரிமையாளர்: முருகன் K', ocr_confidence: 0.96, nlp_confidence: 0.96, final_confidence: 0.96, confidence_category: 'HIGH', validation_status: 'VALID', is_verified: true },
      { id: 'f-2', field_name: 'survey_number', field_value: '123/4A', source_page: 1, raw_ocr_text: 'சர்வே எண்: 123/4A', ocr_confidence: 0.94, nlp_confidence: 0.94, final_confidence: 0.94, confidence_category: 'HIGH', validation_status: 'VALID', is_verified: true },
      { id: 'f-3', field_name: 'area', field_value: '1.45', source_page: 1, raw_ocr_text: 'பரப்பளவு: 1.45 ஹெக்டேர்', ocr_confidence: 0.92, nlp_confidence: 0.92, final_confidence: 0.92, confidence_category: 'HIGH', validation_status: 'VALID', is_verified: true }
    ],
    validations: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 'rec-102',
    document_id: 'doc-002',
    document_type: 'Record of Rights (Form 7/12)',
    state: 'Maharashtra',
    district: 'Pune',
    tehsil: 'Haveli',
    village: 'Wagholi',
    owner_name: 'Ramesh Kumar Sharma',
    parent_name: 'Shyam Lal Sharma',
    survey_number: '124/3A',
    khata_number: '78/B',
    area: 3.5,
    area_unit: 'hectares',
    mutation_number: 'MUT-6381',
    language: 'mr',
    ocr_engine: 'PaddleOCR',
    ocr_confidence: 0.88,
    extraction_confidence: 0.63,
    validation_status: 'WARNING',
    verification_status: 'UNVERIFIED',
    fields: [
      { id: 'f-4', field_name: 'owner_name', field_value: 'Ramesh Kumar Sharma', source_page: 1, raw_ocr_text: 'मालिक: रमेश कुमार शर्मा', ocr_confidence: 0.96, nlp_confidence: 0.96, final_confidence: 0.96, confidence_category: 'HIGH', validation_status: 'VALID', is_verified: false },
      { id: 'f-5', field_name: 'survey_number', field_value: '124/3A', source_page: 1, raw_ocr_text: 'सर्वे नं: 124/3A', ocr_confidence: 0.91, nlp_confidence: 0.91, final_confidence: 0.91, confidence_category: 'HIGH', validation_status: 'VALID', is_verified: false },
      { id: 'f-6', field_name: 'mutation_number', field_value: 'M-2381', source_page: 4, raw_ocr_text: 'नामांतरण: M-2381', ocr_confidence: 0.65, nlp_confidence: 0.63, final_confidence: 0.63, confidence_category: 'LOW', validation_status: 'WARNING', is_verified: false }
    ],
    validations: [
      { id: 'v-1', field_name: 'mutation_number', rule_name: 'mutation_format_check', validation_type: 'format', status: 'WARNING', message: 'Mutation number format unusual (M-2381 instead of MUT-XXXX)', created_at: new Date().toISOString() }
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

export const MOCK_DASHBOARD_STATS: DashboardStats = {
  total_documents: 1248,
  documents_processed: 1240,
  documents_success: 1210,
  documents_failed: 8,
  total_records: 8426,
  high_confidence_records: 7520,
  low_confidence_records: 326,
  records_needing_verification: 326,
  validation_errors_count: 74,
  verified_records_count: 7892,
  exported_records_count: 7892,
  state_distribution: {
    'Tamil Nadu': 3420,
    'Maharashtra': 2150,
    'Uttar Pradesh': 1680,
    'Karnataka': 740,
    'Kerala': 436
  },
  district_distribution: {
    'Coimbatore': 1420,
    'Pune': 1150,
    'Varanasi': 980,
    'Chennai': 850
  },
  language_distribution: {
    'English': 3200,
    'Tamil (தமிழ்)': 2850,
    'Hindi (हिन्दी)': 2376
  },
  validation_status_distribution: {
    'VALID': 7892,
    'WARNING': 460,
    'INVALID': 74
  },
  confidence_distribution: {
    'HIGH (>=0.90)': 7520,
    'MEDIUM (0.70-0.89)': 580,
    'LOW (<0.70)': 326
  },
  error_types: {
    'Format Error': 42,
    'Logical Boundary': 18,
    'Duplicate Record': 14
  }
};
