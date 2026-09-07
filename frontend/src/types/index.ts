export interface DocumentItem {
  id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  expected_language: string;
  detected_language?: string;
  status: 'uploaded' | 'preprocessing' | 'ocr_processing' | 'nlp_extracting' | 'validating' | 'completed' | 'failed';
  total_pages: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessingJob {
  id: string;
  stage: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress_pct: number;
  message?: string;
  started_at: string;
  completed_at?: string;
}

export interface ExtractedField {
  id: string;
  field_name: string;
  field_value?: string;
  source_page: number;
  raw_ocr_text?: string;
  ocr_confidence: number;
  nlp_confidence: number;
  final_confidence: number;
  confidence_category: 'HIGH' | 'MEDIUM' | 'LOW';
  validation_status: 'VALID' | 'WARNING' | 'INVALID' | 'UNVERIFIED';
  original_ai_value?: string;
  verified_value?: string;
  is_verified: boolean;
}

export interface ValidationIssue {
  id: string;
  field_name?: string;
  rule_name: string;
  validation_type: 'format' | 'logical' | 'duplicate' | 'cross_field';
  status: 'VALID' | 'WARNING' | 'INVALID';
  message: string;
  created_at: string;
}

export interface ExtractedRecord {
  id: string;
  document_id: string;
  record_identifier?: string;
  document_type?: string;
  state?: string;
  district?: string;
  tehsil?: string;
  taluk?: string;
  village?: string;
  ward?: string;
  owner_name?: string;
  co_owner_names?: string;
  parent_name?: string;
  ownership_type?: string;
  ownership_share?: string;
  survey_number?: string;
  sub_survey_number?: string;
  khasra_number?: string;
  khata_number?: string;
  plot_number?: string;
  patta_number?: string;
  parcel_id?: string;
  area?: number;
  area_unit?: string;
  land_classification?: string;
  land_type?: string;
  irrigation_status?: string;
  land_use?: string;
  mutation_number?: string;
  mutation_date?: string;
  mutation_type?: string;
  previous_owner?: string;
  new_owner?: string;
  registration_number?: string;
  registration_date?: string;
  deed_number?: string;
  transaction_type?: string;
  record_date?: string;
  source_department?: string;
  language: string;
  ocr_engine: string;
  ocr_confidence: number;
  extraction_confidence: number;
  validation_status: 'VALID' | 'WARNING' | 'INVALID' | 'UNVERIFIED';
  verification_status: 'UNVERIFIED' | 'VERIFIED' | 'REJECTED';
  remarks?: string;
  fields: ExtractedField[];
  validations: ValidationIssue[];
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_documents: number;
  documents_processed: number;
  documents_success: number;
  documents_failed: number;
  total_records: number;
  high_confidence_records: number;
  low_confidence_records: number;
  records_needing_verification: number;
  validation_errors_count: number;
  verified_records_count: number;
  exported_records_count: number;
  state_distribution: Record<string, number>;
  district_distribution: Record<string, number>;
  language_distribution: Record<string, number>;
  validation_status_distribution: Record<string, number>;
  confidence_distribution: Record<string, number>;
  error_types: Record<string, number>;
}

export interface AuditLog {
  id: string;
  user_id?: string;
  user_email?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details_json?: any;
  timestamp: string;
}
