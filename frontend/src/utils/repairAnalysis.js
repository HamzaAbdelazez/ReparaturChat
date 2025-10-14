// Utility functions for repair analysis functionality

export const handleRepairAnalysis = (analysisData, setRepairAnalysis, setShowAnalysis) => {
  if (typeof analysisData === 'boolean') {
    setShowAnalysis(analysisData);
  } else {
    setRepairAnalysis(analysisData);
    setShowAnalysis(true);
  }
};

export const clearAnalysisState = (setRepairAnalysis, setShowAnalysis) => {
  setRepairAnalysis(null);
  setShowAnalysis(false);
};