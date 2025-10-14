import { useState, useEffect, useCallback } from "react";

export const usePdfUpload = (userId) => {
  const [file, setFile] = useState(null);
  const [uploadedPdf, setUploadedPdf] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("not_uploaded");
  const [tools, setTools] = useState([]);

  // Load persistent PDF from localStorage
  useEffect(() => {
    if (!userId) return;
    
    const savedPdf = localStorage.getItem('uploadedPdf');
    if (savedPdf) {
      try {
        const parsedPdf = JSON.parse(savedPdf);
        // Verify PDF belongs to current user before loading
        if (parsedPdf.user_id === userId) {
          setUploadedPdf(parsedPdf);
          setUploadStatus('uploaded');
          loadToolsForPdf(parsedPdf.id);
        } else {
          // PDF belongs to different user, clear it
          localStorage.removeItem('uploadedPdf');
          setUploadedPdf(null);
          setUploadStatus('not_uploaded');
        }
      } catch (error) {
        console.error('Error loading persistent PDF:', error);
        localStorage.removeItem('uploadedPdf');
      }
    }
  }, [userId]);

  // Function to load tools for a specific PDF
  const loadToolsForPdf = useCallback(async (pdfId) => {
    try {
      const res = await fetch(`http://localhost:8000/documents/${pdfId}/tools`);
      if (res.ok) {
        const data = await res.json();
        setTools(data);
      } else {
        console.error("Failed to load tools - response not ok:", res.status);
        setTools([]);
      }
    } catch (err) {
      console.error("Failed to load tools", err);
      setTools([]);
    }
  }, []);

  // Fetch tools when uploadedPdf changes
  useEffect(() => {
    if (!uploadedPdf) {
      setTools([]);
      return;
    }
    loadToolsForPdf(uploadedPdf.id);
  }, [uploadedPdf, loadToolsForPdf]);

  // File Change
  const handleFileChange = useCallback((e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setUploadedPdf(null);
      setUploadStatus("not_uploaded");
    }
  }, []);

  // Upload PDF
  const handleUploadPdf = useCallback(async (currentConversationId) => {
    if (!file || !userId) return;
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploadStatus("uploading");
      const response = await fetch(`http://localhost:8000/uploadedPdfs/?user_id=${userId}`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadedPdf(data);
        setUploadStatus("uploaded");
        
        // Save PDF to localStorage for persistence
        localStorage.setItem('uploadedPdf', JSON.stringify(data));
        
        // Load tools immediately after successful upload
        loadToolsForPdf(data.id);
        
        // If we have a current conversation, save the PDF attachment
        if (currentConversationId) {
          try {
            // Check if this PDF is already attached to avoid duplicates
            const existingMessages = await fetch(`http://localhost:8000/conversations/${currentConversationId}/messages`);
            if (existingMessages.ok) {
              const messages = await existingMessages.json();
              const pdfAlreadyAttached = messages.some(msg => 
                msg.attachment && 
                msg.attachment.type === 'pdf' && 
                msg.attachment.id === data.id
              );
              
              if (!pdfAlreadyAttached) {
                await fetch(`http://localhost:8000/conversations/${currentConversationId}/messages`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    message_type: "system",
                    content: `PDF uploaded: ${data.title}`,
                    attachment: {
                      type: "pdf",
                      id: data.id,
                      filename: data.title
                    }
                  })
                });
              }
            }
          } catch (error) {
            console.error("Failed to save PDF attachment to conversation:", error);
          }
        }
        
        return data;
      } else {
        setUploadStatus("error");
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("error");
    }
  }, [file, userId, loadToolsForPdf]);

  // Delete PDF
  const handleDeletePdf = useCallback(async () => {
    if (!uploadedPdf || !userId) return;
    
    if (!window.confirm(`Are you sure you want to delete "${uploadedPdf.title}"?`)) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/uploadedPdfs/${uploadedPdf.id}?user_id=${userId}`,
        { method: "DELETE" }
      );

      if (response.ok) {
        // Clear PDF-related state and remove from localStorage
        setUploadedPdf(null);
        setFile(null);
        setUploadStatus("not_uploaded");
        setTools([]);
        
        // Remove PDF from localStorage
        localStorage.removeItem('uploadedPdf');
        
        alert("PDF deleted successfully!");
        return true;
      } else {
        const errorData = await response.json();
        alert(`Failed to delete PDF: ${errorData.detail || 'Unknown error'}`);
        return false;
      }
    } catch (error) {
      console.error("Error deleting PDF:", error);
      alert("Failed to delete PDF. Please try again.");
      return false;
    }
  }, [uploadedPdf, userId]);

  const clearPdfState = useCallback(() => {
    setUploadedPdf(null);
    setFile(null);
    setUploadStatus("not_uploaded");
    setTools([]);
  }, []);

  return {
    file,
    uploadedPdf,
    uploadStatus,
    tools,
    setUploadedPdf,
    setUploadStatus,
    setTools,
    handleFileChange,
    handleUploadPdf,
    handleDeletePdf,
    clearPdfState,
    loadToolsForPdf
  };
};