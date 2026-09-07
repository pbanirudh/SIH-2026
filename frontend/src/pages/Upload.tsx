import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileUploader } from '../components/FileUploader';
import { ProcessingPipelineStatus } from '../components/ProcessingPipelineStatus';
import { DocumentItem } from '../types';

export const UploadPage: React.FC = () => {
  const { t } = useTranslation();
  const [uploadedDocs, setUploadedDocs] = useState<DocumentItem[]>([]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">{t('upload.title')}</h2>
        <p className="text-xs text-slate-500 mt-0.5">{t('upload.subtitle')}</p>
      </div>

      <div className={`grid grid-cols-1 ${uploadedDocs.length > 0 ? 'lg:grid-cols-12' : ''} gap-6`}>
        <div className={uploadedDocs.length > 0 ? 'lg:col-span-7' : 'w-full'}>
          <FileUploader onUploadSuccess={(docs) => setUploadedDocs(docs)} />
        </div>

        {uploadedDocs.length > 0 && (
          <div className="lg:col-span-5 flex flex-col gap-4">
            <h3 className="text-sm font-bold text-slate-900">{t('upload.pipeline_title')}</h3>
            {uploadedDocs.map((doc) => (
              <ProcessingPipelineStatus key={doc.id} jobs={[]} currentStatus={doc.status} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
