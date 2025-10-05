import React from "react";

function RepairAnalysis({ 
  uploadedPdf, 
  selectedDevice, 
  userId, 
  showAnalysis, 
  repairAnalysis, 
  onPerformAnalysis 
}) {
  const performRepairAnalysis = async () => {
    if (!uploadedPdf || !selectedDevice) {
      alert("Please upload a document and select a device first.");
      return;
    }

    try {
      onPerformAnalysis(true); // Set loading/show state
      
      // Fetch repair feasibility
      const deviceId = selectedDevice.device_id || selectedDevice.id;
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
      console.error("Error performing repair analysis:", error);
      const errorMessage = error.message || "Unknown error occurred";
      alert(`Failed to perform repair analysis: ${errorMessage}`);
      onPerformAnalysis(false); // Reset loading state
    }
  };

  if (!uploadedPdf || !selectedDevice) {
    return null;
  }

  return (
    <div className="bg-white p-4 rounded-xl shadow-md mb-6">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold">Repair Analysis</h3>
        <button
          onClick={performRepairAnalysis}
          disabled={showAnalysis === true && !repairAnalysis}
          className="bg-purple-500 hover:bg-purple-700 disabled:bg-gray-400 text-white text-sm px-3 py-1 rounded"
        >
          {(showAnalysis === true && !repairAnalysis) ? "Analyzing..." : "Analyze Repair"}
        </button>
      </div>
      
      {showAnalysis && repairAnalysis && (
        <div className="space-y-4">
          {/* Feasibility */}
          {repairAnalysis.feasibility && (
            <div className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-medium">Repair Feasibility</h4>
              <p className={`text-sm ${repairAnalysis.feasibility.is_feasible ? "text-green-600" : "text-red-600"}`}>
                {repairAnalysis.feasibility.is_feasible ? "[YES] You can perform this repair" : "[NO] This repair may be too complex"}
              </p>
              <p className="text-xs text-gray-600">
                Your skill: {repairAnalysis.feasibility.user_skill_score}/5 | Required: {repairAnalysis.feasibility.required_skill_score}/5
              </p>
              {repairAnalysis.feasibility.warnings.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-orange-600">Warnings:</p>
                  <ul className="text-xs text-orange-600 list-disc list-inside">
                    {repairAnalysis.feasibility.warnings.map((warning, idx) => (
                      <li key={idx}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}
              {repairAnalysis.feasibility.recommendations.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-blue-600">Recommendations:</p>
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
          {repairAnalysis.costs && repairAnalysis.time && (
            <div className="border-l-4 border-green-500 pl-4">
              <h4 className="font-medium">Cost & Time Estimate</h4>
              <p className="text-sm">
                [COST] Total Cost: €{repairAnalysis.costs.total_cost.toFixed(2)} 
                (Tools: €{repairAnalysis.costs.tools_cost.toFixed(2)}, Parts: €{repairAnalysis.costs.parts_cost.toFixed(2)})
              </p>
              <p className="text-sm">
                [TIME] Estimated Time: {repairAnalysis.time.total_time_hours.toFixed(1)} hours
              </p>
              {repairAnalysis.costs.tool_details && repairAnalysis.costs.tool_details.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-gray-700">Tool Details:</p>
                  <ul className="text-xs text-gray-600 list-disc list-inside">
                    {repairAnalysis.costs.tool_details.map((tool, idx) => (
                      <li key={idx}>
                        {tool.name}: €{tool.price.toFixed(2)} (Reusability: {tool.reusability_score}/5)
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Comparison */}
          {repairAnalysis.comparison && (
            <div className="border-l-4 border-yellow-500 pl-4">
              <h4 className="font-medium">Self-Repair vs Professional</h4>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="font-medium">Self-Repair:</p>
                  <p>Cost: €{repairAnalysis.comparison.self_repair.cost.toFixed(2)}</p>
                  <p>Time: {repairAnalysis.comparison.self_repair.time.toFixed(1)}h</p>
                  <p className={`text-xs ${repairAnalysis.comparison.self_repair.feasible ? "text-green-600" : "text-red-600"}`}>
                    {repairAnalysis.comparison.self_repair.feasible ? "[YES] Feasible" : "[NO] Not recommended"}
                  </p>
                </div>
                <div>
                  <p className="font-medium">Professional:</p>
                  <p>Cost: €{repairAnalysis.comparison.professional_service.cost.toFixed(2)}</p>
                  <p>Time: {repairAnalysis.comparison.professional_service.time.toFixed(1)}h</p>
                  <p className="text-xs text-green-600">[YES] Guaranteed</p>
                </div>
              </div>
              <p className={`text-sm font-medium mt-2 ${
                repairAnalysis.comparison.recommendation === "self_repair" ? "text-green-600" : "text-blue-600"
              }`}>
[RECOMMEND] {repairAnalysis.comparison.recommendation === "self_repair" ? "Do it yourself" : "Use professional service"}
              </p>
              <div className="mt-2 text-xs text-gray-600">
                <p>Cost difference: €{repairAnalysis.comparison.cost_difference.toFixed(2)}</p>
                <p>Time difference: {repairAnalysis.comparison.time_difference.toFixed(1)}h</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RepairAnalysis;