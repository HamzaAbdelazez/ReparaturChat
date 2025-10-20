import React from "react";
import { useTranslation } from "react-i18next";
import { Wrench, X, RefreshCw } from "lucide-react";

function DocumentUpload({ 
  file, 
  uploadStatus, 
  uploadedPdf, 
  onFileChange, 
  onUpload,
  onDelete
}) {
  const { t } = useTranslation();
  return (
    <div className="mb-6">
      {/* PDF Upload Section */}
      <label className="custum-file-upload">
        <div className="icon">
          <Wrench className="w-12 h-12 text-blue-600" />
        </div>
        <div className="text">
          <span>{file ? file.name : t('upload.clickToUpload')}</span>
        </div>
        <input
          type="file"
          accept="application/pdf"
          onChange={onFileChange}
        />
      </label>

      <div className="mt-3 flex justify-center gap-2">
        <button
          onClick={onUpload}
          disabled={uploadStatus === "uploading" || !file}
          className={`bg-blue-500 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded flex items-center gap-2 ${
            uploadStatus === "uploading" || !file
              ? "opacity-50 cursor-not-allowed"
              : ""
          }`}
        >
          {uploadStatus === "uploading" && (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          )}
          {uploadStatus === "uploading" ? t('upload.processingPdf') : uploadedPdf ? t('upload.replacePdf') : t('upload.uploadPdf')}
        </button>
        
        {uploadedPdf && (
          <button
            onClick={onDelete}
            className="bg-red-500 hover:bg-red-700 text-white text-sm font-semibold py-2 px-3 rounded flex items-center gap-1"
          >
            <X size={16} /> {t('upload.delete')}
          </button>
        )}
      </div>

      {/* PDF Status */}
      <div className="mt-2 text-sm text-center">
        {uploadStatus === "uploaded" && uploadedPdf && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-green-700">
            <div className="flex items-center justify-center gap-2">
              <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
              <span className="font-medium">{t('upload.ready')}</span>
            </div>
            <div className="text-xs mt-1">PDF: {uploadedPdf.title}</div>
          </div>
        )}
        {uploadStatus === "uploading" && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-blue-700">
            <div className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span>{t('upload.processingPdf')}</span>
            </div>
            <div className="text-xs mt-1">{t('upload.extractingTools')}</div>
          </div>
        )}
        {uploadStatus === "error" && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700">
            <div className="flex items-center justify-center gap-2">
              <span className="text-red-500">⚠️</span>
              <span>{t('upload.uploadFailed')}</span>
            </div>
          </div>
        )}
        {uploadStatus === "not_uploaded" && file && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2 text-yellow-700">
            <span>{t('upload.readyToUpload', { filename: file.name })}</span>
          </div>
        )}
      </div>

    </div>
  );
}

export default DocumentUpload;