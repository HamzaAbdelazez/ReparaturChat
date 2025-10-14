import { useTranslation } from "react-i18next";

function RepairAnalysis({ 
  uploadedPdf, 
  selectedDevice, 
  userId, 
  showAnalysis, 
  repairAnalysis, 
  onPerformAnalysis,
  chatHistory 
}) {
  const { t } = useTranslation();

  // Extract problem description from chat history
  const extractProblemFromChat = () => {
    if (!chatHistory || chatHistory.length === 0) return null;
    
    // Get the last user message that might contain a problem description
    const userMessages = chatHistory.filter(msg => msg.type === 'user');
    if (userMessages.length === 0) return null;
    
    // Always use the most recent user message as the problem description
    // This allows continuous analysis after each new message
    const recentMessage = userMessages[userMessages.length - 1];
    
    // Accept any message that has meaningful content (at least 5 characters)
    if (recentMessage && recentMessage.content.trim().length >= 5) {
      return recentMessage.content;
    }
    
    // If the latest message is too short, combine recent messages
    if (userMessages.length >= 2) {
      const lastTwoMessages = userMessages.slice(-2).map(msg => msg.content).join('. ');
      return lastTwoMessages.trim().length >= 10 ? lastTwoMessages : null;
    }
    
    return null;
  };

  // Perform repair analysis based on chat problem description with automatic device detection
  const performChatBasedAnalysis = async () => {
    const problemDescription = extractProblemFromChat();
    
    if (!problemDescription) {
      // If no description found, still try to analyze with a generic message
      const fallbackDescription = "Device troubleshooting and repair analysis";
      console.log('No specific problem description found, using fallback');
    }

    try {
      onPerformAnalysis(true); // Set loading state
      
      // Call the new chat-based analysis endpoint without requiring device_id
      const analysisResponse = await fetch(
        `http://localhost:8000/repair-analysis/chat-based-analysis`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: userId,
            problem_description: problemDescription || "Device troubleshooting and repair analysis",
            chat_history: chatHistory.slice(-10), // Send last 10 messages for context
            document_id: uploadedPdf?.id || null // Include PDF ID if available for device extraction
          })
        }
      );
      
      if (!analysisResponse.ok) {
        throw new Error(`Analysis failed: ${analysisResponse.status}`);
      }
      
      const analysisResult = await analysisResponse.json();
      onPerformAnalysis(analysisResult);
      
    } catch (error) {
      console.error("Error performing chat-based repair analysis:", error);
      alert(t('analysis.analysisError', { error: error.message }));
      onPerformAnalysis(false);
    }
  };

  // Original PDF-based analysis (keep for backward compatibility)
  const performPdfBasedAnalysis = async () => {
    if (!uploadedPdf || !selectedDevice) {
      alert(t('analysis.uploadAndSelectDevice'));
      return;
    }

    try {
      onPerformAnalysis(true);
      
      const deviceId = selectedDevice.device_id || selectedDevice.id;
      
      // Fetch repair feasibility
      const feasibilityResponse = await fetch(
        `http://localhost:8000/repair-analysis/feasibility?user_id=${userId}&device_id=${deviceId}&document_id=${uploadedPdf.id}`
      );
      
      if (!feasibilityResponse.ok) {
        throw new Error(`Feasibility check failed: ${feasibilityResponse.status}`);
      }
      const feasibility = await feasibilityResponse.json();

      // Fetch cost estimation
      const costResponse = await fetch(
        `http://localhost:8000/repair-analysis/cost-estimation?user_id=${userId}&document_id=${uploadedPdf.id}`
      );
      
      if (!costResponse.ok) {
        throw new Error(`Cost estimation failed: ${costResponse.status}`);
      }
      const costs = await costResponse.json();

      // Fetch time estimation
      const timeResponse = await fetch(
        `http://localhost:8000/repair-analysis/time-estimation?user_id=${userId}&document_id=${uploadedPdf.id}`
      );
      
      if (!timeResponse.ok) {
        throw new Error(`Time estimation failed: ${timeResponse.status}`);
      }
      const time = await timeResponse.json();

      // Fetch comparison
      const comparisonResponse = await fetch(
        `http://localhost:8000/repair-analysis/compare-options?user_id=${userId}&device_id=${deviceId}&document_id=${uploadedPdf.id}`
      );
      
      if (!comparisonResponse.ok) {
        throw new Error(`Comparison failed: ${comparisonResponse.status}`);
      }
      const comparison = await comparisonResponse.json();

      onPerformAnalysis({
        feasibility,
        costs,
        time,
        comparison
      });
    } catch (error) {
      console.error("Error performing PDF-based repair analysis:", error);
      alert(t('analysis.analysisError', { error: error.message }));
      onPerformAnalysis(false);
    }
  };

  // Determine if we should show the component
  const problemDescription = extractProblemFromChat();
  const hasChatContent = chatHistory && chatHistory.length > 0;
  const hasDevice = selectedDevice != null;
  
  // Show if we have chat content (device will be auto-detected), or if we have PDF
  const shouldShow = hasChatContent || uploadedPdf;
  
  if (!shouldShow) {
    return null;
  }

  return (
    <div className="bg-white p-4 rounded-xl shadow-md mb-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold">{t('analysis.title')}</h3>
        
        <div className="flex gap-2">
          {/* Chat-based analysis button - no device selection required */}
          {hasChatContent && (
            <button
              onClick={performChatBasedAnalysis}
              disabled={showAnalysis === true && !repairAnalysis}
              className="bg-blue-500 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm px-3 py-1 rounded flex items-center gap-1"
            >
              <span>💬</span>
              {(showAnalysis === true && !repairAnalysis) ? t('analysis.analyzing') : t('analysis.analyzeFromChat')}
            </button>
          )}
          
          {/* PDF-based analysis button */}
          {uploadedPdf && hasDevice && (
            <button
              onClick={performPdfBasedAnalysis}
              disabled={showAnalysis === true && !repairAnalysis}
              className="bg-purple-500 hover:bg-purple-700 disabled:bg-gray-400 text-white text-sm px-3 py-1 rounded flex items-center gap-1"
            >
              <span>📄</span>
              {(showAnalysis === true && !repairAnalysis) ? t('analysis.analyzing') : t('analysis.analyzeFromPdf')}
            </button>
          )}
        </div>
      </div>
      
      {/* Show current analysis mode */}
      <div className="mb-3 text-xs text-gray-600">
        {problemDescription && (
          <div className="bg-blue-50 border border-blue-200 rounded p-2 mb-2">
            <p className="font-medium text-blue-800">{t('analysis.detectedProblem')}:</p>
            <p className="text-blue-700">"{problemDescription.length > 100 ? problemDescription.substring(0, 97) + '...' : problemDescription}"</p>
          </div>
        )}
        
        {uploadedPdf && (
          <div className="bg-purple-50 border border-purple-200 rounded p-2 mb-2">
            <p className="font-medium text-purple-800">{t('analysis.pdfAvailable')}: {uploadedPdf.title}</p>
          </div>
        )}
        
        {hasDevice && (
          <div className="bg-green-50 border border-green-200 rounded p-2">
            <p className="font-medium text-green-800">{t('analysis.selectedDevice')}: {selectedDevice.manufacturer} {selectedDevice.model}</p>
          </div>
        )}
        
        {!hasDevice && hasChatContent && (
          <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
            <p className="font-medium text-yellow-800">{t('analysis.autoDetectDevice')}</p>
          </div>
        )}
      </div>
      
      {showAnalysis && repairAnalysis && (
        <div className="space-y-4">
          {/* Analysis source and device info */}
          {repairAnalysis.analysis_source && (
            <div className="text-xs text-gray-500 italic">
              {t('analysis.analysisSource')}: {repairAnalysis.analysis_source}
            </div>
          )}
          
          {/* Extracted device information */}
          {repairAnalysis.device_info && (
            <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
              <h4 className="font-medium text-blue-800 mb-2">{t('analysis.detectedDevice')}:</h4>
              <div className="text-sm text-blue-700">
                <p><strong>{t('analysis.manufacturer')}:</strong> {repairAnalysis.device_info.manufacturer}</p>
                <p><strong>{t('analysis.model')}:</strong> {repairAnalysis.device_info.model}</p>
                <p><strong>{t('analysis.category')}:</strong> {repairAnalysis.device_info.category}</p>
                {repairAnalysis.device_info.confidence > 0 && (
                  <p><strong>{t('analysis.confidence')}:</strong> {repairAnalysis.device_info.confidence}%</p>
                )}
                {repairAnalysis.device_info.extracted_text && (
                  <p className="text-xs italic mt-1">
                    <strong>{t('analysis.extractedFrom')}:</strong> "{repairAnalysis.device_info.extracted_text}"
                  </p>
                )}
                <p className="text-xs mt-1">
                  <strong>{t('analysis.detectionSource')}:</strong> {repairAnalysis.device_info.source}
                </p>
              </div>
            </div>
          )}
          
          {/* Feasibility */}
          {repairAnalysis.feasibility && (
            <div className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-medium">{t('analysis.repairFeasibility')}</h4>
              <p className={`text-sm ${repairAnalysis.feasibility.is_feasible ? "text-green-600" : "text-red-600"}`}>
                {repairAnalysis.feasibility.is_feasible ? t('analysis.feasibleYes') : t('analysis.feasibleNo')}
              </p>
              <p className="text-xs text-gray-600">
                {t('analysis.skillComparison', {
                  userSkill: repairAnalysis.feasibility.user_skill_score || 'N/A',
                  requiredSkill: repairAnalysis.feasibility.required_skill_score || 'N/A'
                })}
              </p>
              {repairAnalysis.feasibility.warnings && repairAnalysis.feasibility.warnings.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-orange-600">{t('analysis.warnings')}:</p>
                  <ul className="text-xs text-orange-600 list-disc list-inside">
                    {repairAnalysis.feasibility.warnings.map((warning, idx) => (
                      <li key={idx}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
              {repairAnalysis.feasibility.recommendations && repairAnalysis.feasibility.recommendations.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-blue-600">{t('analysis.recommendations')}:</p>
                  <ul className="text-xs text-blue-600 list-disc list-inside">
                    {repairAnalysis.feasibility.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Cost & Time */}
          {(repairAnalysis.costs || repairAnalysis.cost_estimate) && (
            <div className="border-l-4 border-green-500 pl-4">
              <h4 className="font-medium">{t('analysis.costTimeEstimate')}</h4>
              {repairAnalysis.costs && (
                <>
                  <p className="text-sm">
                    {t('analysis.totalCost')}: €{repairAnalysis.costs.total_cost.toFixed(2)} 
                    ({t('analysis.tools')}: €{repairAnalysis.costs.tools_cost.toFixed(2)}, {t('analysis.parts')}: €{repairAnalysis.costs.parts_cost.toFixed(2)})
                  </p>
                  {repairAnalysis.time && (
                    <p className="text-sm">
                      {t('analysis.estimatedTime')}: {repairAnalysis.time.total_time_hours.toFixed(1)} {t('analysis.hours')}
                    </p>
                  )}
                </>
              )}
              {repairAnalysis.cost_estimate && (
                <p className="text-sm">
                  {t('analysis.estimatedCostRange')}: €{repairAnalysis.cost_estimate}
                </p>
              )}
              {repairAnalysis.time_estimate && (
                <p className="text-sm">
                  {t('analysis.estimatedTimeRange')}: {repairAnalysis.time_estimate}
                </p>
              )}
            </div>
          )}

          {/* Comparison */}
          {repairAnalysis.comparison && (
            <div className="border-l-4 border-yellow-500 pl-4">
              <h4 className="font-medium">{t('analysis.selfRepairVsProfessional')}</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="font-medium">{t('analysis.selfRepair')}:</p>
                  <p>{t('analysis.cost')}: €{typeof repairAnalysis.comparison.self_repair.cost === 'number' ? repairAnalysis.comparison.self_repair.cost.toFixed(2) : repairAnalysis.comparison.self_repair.cost}</p>
                  <p>{t('analysis.time')}: {typeof repairAnalysis.comparison.self_repair.time === 'number' ? repairAnalysis.comparison.self_repair.time.toFixed(1) + 'h' : repairAnalysis.comparison.self_repair.time}</p>
                  <p className={`text-xs ${repairAnalysis.comparison.self_repair.feasible ? "text-green-600" : "text-red-600"}`}>
                    {repairAnalysis.comparison.self_repair.feasible ? t('analysis.feasible') : t('analysis.notRecommended')}
                  </p>
                </div>
                <div>
                  <p className="font-medium">{t('analysis.professional')}:</p>
                  <p>{t('analysis.cost')}: €{typeof repairAnalysis.comparison.professional_service.cost === 'number' ? repairAnalysis.comparison.professional_service.cost.toFixed(2) : repairAnalysis.comparison.professional_service.cost}</p>
                  <p>{t('analysis.time')}: {typeof repairAnalysis.comparison.professional_service.time === 'number' ? repairAnalysis.comparison.professional_service.time.toFixed(1) + 'h' : repairAnalysis.comparison.professional_service.time}</p>
                  <p className="text-xs text-green-600">{t('analysis.guaranteed')}</p>
                </div>
              </div>
              <p className={`text-sm font-medium mt-2 ${
                repairAnalysis.comparison.recommendation === "self_repair" ? "text-green-600" : "text-blue-600"
              }`}>
                {t('analysis.recommendation')}: {repairAnalysis.comparison.recommendation === "self_repair" ? t('analysis.doItYourself') : t('analysis.useProfessional')}
              </p>
            </div>
          )}

          {/* Additional analysis info from chat-based analysis */}
          {repairAnalysis.problem_summary && (
            <div className="border-l-4 border-indigo-500 pl-4">
              <h4 className="font-medium">{t('analysis.problemSummary')}</h4>
              <p className="text-sm text-gray-700">{repairAnalysis.problem_summary}</p>
            </div>
          )}

          {repairAnalysis.suggested_solutions && repairAnalysis.suggested_solutions.length > 0 && (
            <div className="border-l-4 border-teal-500 pl-4">
              <h4 className="font-medium">{t('analysis.suggestedSolutions')}</h4>
              <ul className="text-sm text-gray-700 list-disc list-inside">
                {repairAnalysis.suggested_solutions.map((solution, idx) => (
                  <li key={idx}>{solution}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RepairAnalysis;