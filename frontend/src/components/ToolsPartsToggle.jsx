import { useState, useEffect } from 'react';
import { Settings, Wrench, Eye, EyeOff } from 'lucide-react';

const ToolsPartsToggle = ({ userId, onPreferenceChange, disabled = false }) => {
  const [showToolsParts, setShowToolsParts] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Load user preference on component mount
  useEffect(() => {
    if (userId) {
      loadUserPreference();
    }
  }, [userId]);

  const loadUserPreference = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/user-preferences/tools-parts?user_id=${userId}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setShowToolsParts(data.show_tools_parts);
        if (onPreferenceChange) {
          onPreferenceChange(data.show_tools_parts);
        }
      }
    } catch (error) {
      console.error('Failed to load user preference:', error);
    }
  };

  const updatePreference = async (newValue) => {
    if (!userId) return;

    setIsLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/user-preferences/tools-parts?user_id=${userId}&show_tools_parts=${newValue}`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        setShowToolsParts(newValue);
        if (onPreferenceChange) {
          onPreferenceChange(newValue);
        }
      }
    } catch (error) {
      console.error('Failed to update user preference:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = () => {
    if (!disabled && !isLoading) {
      const newValue = !showToolsParts;
      updatePreference(newValue);
    }
  };

  return (
    <div className="relative">
      {/* Main Toggle Button */}
      <button
        onClick={() => setShowSettings(!showSettings)}
        disabled={disabled}
        className={`
          flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200 text-sm
          ${disabled 
            ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed' 
            : 'bg-white border-gray-300 hover:border-gray-400 cursor-pointer'
          }
        `}
        title={disabled ? 'Settings disabled during chat' : 'Tools & Parts Settings'}
      >
        <Wrench className={`w-4 h-4 ${disabled ? 'text-gray-400' : 'text-blue-600'}`} />
        <span className="text-gray-700">Tools & Parts</span>
        {showToolsParts ? (
          <Eye className={`w-4 h-4 ${disabled ? 'text-gray-400' : 'text-green-600'}`} />
        ) : (
          <EyeOff className={`w-4 h-4 ${disabled ? 'text-gray-400' : 'text-red-600'}`} />
        )}
        <Settings className={`w-4 h-4 transition-transform ${showSettings ? 'rotate-90' : ''} ${disabled ? 'text-gray-400' : 'text-gray-500'}`} />
      </button>

      {/* Settings Dropdown */}
      {showSettings && !disabled && (
        <div className="absolute top-full left-0 mt-1 w-72 bg-white border border-gray-200 rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="p-3 bg-gray-50 border-b border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <Wrench className="w-4 h-4 text-blue-600" />
              Tools & Parts Display
            </h3>
          </div>
          
          <div className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="text-sm font-medium text-gray-900">
                  Show Tools & Parts Information
                </h4>
                <p className="text-xs text-gray-500 mt-1">
                  Display required tools and parts in AI responses
                </p>
              </div>
              
              <button
                onClick={handleToggle}
                disabled={isLoading}
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent 
                  transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                  ${showToolsParts ? 'bg-blue-600' : 'bg-gray-200'}
                  ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 
                    transition duration-200 ease-in-out
                    ${showToolsParts ? 'translate-x-5' : 'translate-x-0'}
                  `}
                />
              </button>
            </div>
            
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 flex-shrink-0" />
                <div className="text-xs text-blue-700">
                  <p className="font-medium">What this includes:</p>
                  <ul className="mt-1 space-y-0.5">
                    <li>• Required tools (screwdrivers, multimeters, etc.)</li>
                    <li>• Replacement parts (batteries, screens, etc.)</li>
                    <li>• Estimated costs when available</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolsPartsToggle;