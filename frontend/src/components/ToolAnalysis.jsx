import React from "react";
import { useTranslation } from "react-i18next";

function ToolAnalysis({ tools, userId, onAnalyzeToolReusability }) {
  const { t } = useTranslation();
  const [loadingTools, setLoadingTools] = React.useState({});

  const analyzeToolReusability = async (toolId) => {
    if (!userId) {
      alert(t('errors.loginRequired'));
      return;
    }

    setLoadingTools(prev => ({ ...prev, [toolId]: true }));

    try {
      // Get detailed breakdown
      const breakdownResponse = await fetch(
        `http://localhost:8000/repair-analysis/tool-reusability-breakdown/${toolId}?user_id=${userId}`
      );
      
      if (breakdownResponse.ok) {
        const breakdown = await breakdownResponse.json();
        
        // Get reusability analysis
        const analysisResponse = await fetch(
          `http://localhost:8000/repair-analysis/tool-reusability/${toolId}?user_id=${userId}`
        );
        
        if (analysisResponse.ok) {
          const analysis = await analysisResponse.json();
          
          const message = `Tool Reusability Analysis: ${breakdown.tool_name}

Compatibility Score: ${breakdown.compatibility_score}/5
Estimated Future Uses: ${breakdown.estimated_future_uses}
Cost per Use: €${breakdown.cost_per_use}

Your Profile:
- Skill Level: ${breakdown.user_skill_level}/5
- Experience Level: ${breakdown.user_experience_level}/5
- Compatible Devices: ${breakdown.user_devices_count}

Recommendation: ${analysis.recommendation.toUpperCase()}
${analysis.recommendation === 'buy' ? '✅ Good investment' : 
  analysis.recommendation === 'rent' ? '📅 Consider renting' : 
  analysis.recommendation === 'borrow' ? '🤝 Try to borrow' : 
  '📚 Consider training first'}

Overall Reusability Score: ${analysis.reusability_score}/5`;

          alert(message);
        }
      }
    } catch (error) {
      console.error("Error analyzing tool reusability:", error);
      alert(t('errors.analyzeToolFailed'));
    } finally {
      setLoadingTools(prev => ({ ...prev, [toolId]: false }));
    }
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-md mb-6">
      <h3 className="text-lg font-semibold mb-2">{t('tools.title')}</h3>
      {tools.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-4xl mb-2">🛠️</div>
          <p className="text-gray-500 font-medium">{t('tools.noToolsExtracted')}</p>
          <p className="text-sm text-gray-400 mt-1">
            {t('tools.noToolsDescription')}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {tools.map((tool) => (
            <div key={tool.id} className="border rounded p-3">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-medium">🛠 {tool.name}</p>
                  {tool.reusability_score && (
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-gray-600">{t('tools.reusability')}:</span>
                      <div className="flex">
                        {[1, 2, 3, 4, 5].map((num) => (
                          <span
                            key={num}
                            className={`text-xs ${
                              num <= tool.reusability_score ? "text-green-500" : "text-gray-300"
                            }`}
                          >
                            ★
                          </span>
                        ))}
                      </div>
                      <span className="text-xs text-gray-500">({tool.reusability_score}/5)</span>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => analyzeToolReusability(tool.id)}
                  disabled={loadingTools[tool.id]}
                  className={`text-xs px-2 py-1 rounded flex items-center gap-1 ${
                    loadingTools[tool.id] 
                      ? "bg-gray-400 cursor-not-allowed" 
                      : "bg-blue-500 hover:bg-blue-600 text-white"
                  }`}
                >
                  {loadingTools[tool.id] && (
                    <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin"></div>
                  )}
                  {loadingTools[tool.id] ? t('tools.analyzing') : t('tools.analyze')}
                </button>
              </div>
              {tool.min_price && (
                <p className="text-sm text-gray-600">
                  {t('tools.price', { 
                    min: tool.min_price.toFixed(2), 
                    range: tool.max_price && tool.max_price !== tool.min_price ? ` - €${tool.max_price.toFixed(2)}` : '' 
                  })}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ToolAnalysis;