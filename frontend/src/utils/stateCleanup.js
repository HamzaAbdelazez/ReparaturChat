// Utility functions for cleaning up application state

export const clearAllState = ({
  setUserId,
  setUploadedPdf,
  setFile,
  setUploadStatus,
  setHistory,
  setTools,
  setUserDevices,
  setSelectedDevice,
  setRepairAnalysis,
  setConversations,
  setCurrentConversationId,
  setShowAnalysis,
  setShowDeviceManager
}) => {
  setUserId(null);
  setUploadedPdf(null);
  setFile(null);
  setUploadStatus("not_uploaded");
  setHistory([]);
  setTools([]);
  setUserDevices([]);
  setSelectedDevice(null);
  setRepairAnalysis(null);
  setConversations([]);
  setCurrentConversationId(null);
  setShowAnalysis(false);
  setShowDeviceManager(false);
};

export const clearConversationState = ({
  setHistory,
  setRepairAnalysis,
  setShowAnalysis,
  clearPdfState
}) => {
  setHistory([]);
  setRepairAnalysis(null);
  setShowAnalysis(false);
  clearPdfState();
};