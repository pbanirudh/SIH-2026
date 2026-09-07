import React from 'react';
import { CheckCircle2, Clock, Loader2, AlertCircle } from 'lucide-react';
import { ProcessingJob } from '../types';

interface ProcessingPipelineStatusProps {
  jobs: ProcessingJob[];
  currentStatus: string;
}

const STAGES = [
  { id: 'upload', label: 'Document Upload' },
  { id: 'preprocessing', label: 'Image/PDF Preprocessing' },
  { id: 'classification', label: 'Document Classification' },
  { id: 'ocr', label: 'PaddleOCR Text Detection' },
  { id: 'trocr', label: 'Indic-TrOCR Handwriting' },
  { id: 'layout', label: 'Layout & Table Analysis' },
  { id: 'nlp', label: 'NLP Entity Extraction' },
  { id: 'validation', label: 'Validation Engine' },
  { id: 'verification', label: 'Human Verification' },
];

export const ProcessingPipelineStatus: React.FC<ProcessingPipelineStatusProps> = ({ jobs, currentStatus }) => {
  const getStageStatus = (stageId: string) => {
    if (currentStatus === 'failed') return 'failed';
    
    // Check if jobs contain completed stage
    const stageJob = jobs.find((j) => j.stage === stageId);
    if (stageJob) return stageJob.status;

    if (currentStatus === 'completed') return 'completed';

    // Heuristic stage progression
    const stageOrder = ['upload', 'preprocessing', 'classification', 'ocr', 'trocr', 'layout', 'nlp', 'validation', 'verification'];
    const currentIdx = stageOrder.indexOf(currentStatus.replace('_processing', '').replace('_extracting', ''));
    const stageIdx = stageOrder.indexOf(stageId);

    if (currentIdx > stageIdx) return 'completed';
    if (currentIdx === stageIdx) return 'in_progress';
    return 'pending';
  };

  return (
    <div className="glass-panel" style={{ padding: '20px' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', color: '#f8fafc' }}>
        Processing Pipeline Status
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {STAGES.map((stg) => {
          const status = getStageStatus(stg.id);
          return (
            <div
              key={stg.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '6px',
                background: status === 'in_progress' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(15, 23, 42, 0.4)',
                border: status === 'in_progress' ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid rgba(255, 255, 255, 0.05)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {status === 'completed' && <CheckCircle2 size={18} color="#10b981" />}
                {status === 'in_progress' && <Loader2 size={18} color="#3b82f6" className="animate-spin" />}
                {status === 'pending' && <Clock size={18} color="#64748b" />}
                {status === 'failed' && <AlertCircle size={18} color="#ef4444" />}
                <span style={{
                  fontSize: '0.85rem',
                  fontWeight: status === 'in_progress' ? 600 : 400,
                  color: status === 'completed' ? '#34d399' : status === 'in_progress' ? '#60a5fa' : '#94a3b8'
                }}>
                  {stg.label}
                </span>
              </div>

              <span style={{
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                fontWeight: 600,
                color: status === 'completed' ? '#10b981' : status === 'in_progress' ? '#3b82f6' : '#64748b'
              }}>
                {status === 'completed' ? 'Done' : status === 'in_progress' ? 'Active' : status === 'failed' ? 'Error' : 'Pending'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
