import React from "react";
import { Wrench, X, RefreshCw } from "lucide-react";

function DocumentUpload({ 
  file, 
  uploadStatus, 
  uploadedPdf, 
  onFileChange, 
  onUpload,
  onDelete,
  chatMode,
  onChatModeChange
}) {
  return (
    <div className="mb-6">
      {/* PDF Upload Section */}
      <label className="custum-file-upload">
        <div className="icon">
          <Wrench className="w-12 h-12 text-blue-600" />
        </div>
        <div className="text">
          <span>{file ? file.name : "Click to upload your PDF"}</span>
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
          className={`bg-blue-500 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded ${
            uploadStatus === "uploading" || !file
              ? "opacity-50 cursor-not-allowed"
              : ""
          }`}
        >
          {uploadStatus === "uploading" ? "Uploading..." : uploadedPdf ? "Replace PDF" : "Upload"}
        </button>
        
        {uploadedPdf && (
          <button
            onClick={onDelete}
            className="bg-red-500 hover:bg-red-700 text-white text-sm font-semibold py-2 px-3 rounded flex items-center gap-1"
          >
            <X size={16} /> Delete
          </button>
        )}
      </div>

      {/* PDF Status */}
      <div className="mt-2 text-sm text-center">
        {uploadStatus === "uploaded" && uploadedPdf && (
          <div className="text-green-600 mb-2">
            ✅ Uploaded: {uploadedPdf.title}
          </div>
        )}
        {uploadStatus === "uploading" && (
          <span className="text-blue-600">⏳ Uploading...</span>
        )}
        {uploadStatus === "error" && (
          <span className="text-red-600">❌ Upload failed</span>
        )}
        {uploadStatus === "not_uploaded" && file && (
          <span className="text-gray-600">⚠️ Not uploaded yet</span>
        )}
      </div>

      {/* Chat Mode Selector - only show when PDF is uploaded */}
      {uploadedPdf && (
        <div className="mt-4 p-3 bg-gray-50 rounded border">
          <div className="text-sm font-medium text-gray-700 mb-2">Chat Mode:</div>
          <div className="flex gap-2 text-sm">
            <button
              onClick={() => onChatModeChange("pdf")}
              className={`px-3 py-1 rounded ${
                chatMode === "pdf"
                  ? "bg-blue-500 text-white"
                  : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
              }`}
            >
              📄 PDF Chat
            </button>
            <button
              onClick={() => onChatModeChange("general")}
              className={`px-3 py-1 rounded ${
                chatMode === "general"
                  ? "bg-green-500 text-white"
                  : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50"
              }`}
            >
              💬 General Chat
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {chatMode === "pdf" 
              ? "Ask questions about the uploaded PDF"
              : "Ask general questions (not about the PDF)"
            }
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;