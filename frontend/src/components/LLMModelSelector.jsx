import { useState, useEffect } from 'react';
import { Settings, Zap, Brain, Cpu, Sparkles } from 'lucide-react';

const LLMModelSelector = ({ selectedModel, onModelChange, disabled = false }) => {
  const [isOpen, setIsOpen] = useState(false);

  const models = [
    {
      id: 'gemma3',
      name: 'Gemma 3',
      description: 'Fast and reliable via Replicate',
      icon: Zap,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50 hover:bg-blue-100'
    },
    {
      id: 'gemini',
      name: 'Gemini Pro',
      description: 'Advanced reasoning by Google',
      icon: Brain,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50 hover:bg-purple-100'
    },
    {
      id: 'deepseek',
      name: 'DeepSeek-R1',
      description: 'Advanced reasoning model via Replicate',
      icon: Cpu,
      color: 'text-green-600',
      bgColor: 'bg-green-50 hover:bg-green-100'
    },
    {
      id: 'gpt5',
      name: 'GPT-5',
      description: 'Latest OpenAI model via Replicate',
      icon: Sparkles,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50 hover:bg-orange-100'
    }
  ];

  const selectedModelData = models.find(m => m.id === selectedModel) || models[0];
  const SelectedIcon = selectedModelData.icon;

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.llm-selector-dropdown')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className="relative llm-selector-dropdown">
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200
          ${disabled 
            ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed' 
            : 'bg-white border-gray-300 hover:border-gray-400 cursor-pointer'
          }
          ${selectedModelData.bgColor.split(' ')[0]} text-sm font-medium
        `}
        title={disabled ? 'Model selection is disabled during chat' : 'Change AI Model'}
      >
        <SelectedIcon className={`w-4 h-4 ${selectedModelData.color}`} />
        <span className="text-gray-700">{selectedModelData.name}</span>
        <Settings className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-90' : ''} ${disabled ? 'text-gray-400' : 'text-gray-500'}`} />
      </button>

      {isOpen && !disabled && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="p-2 bg-gray-50 border-b border-gray-200">
            <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              AI Model Selection
            </h3>
          </div>
          
          <div className="py-1">
            {models.map((model) => {
              const IconComponent = model.icon;
              const isSelected = model.id === selectedModel;
              
              return (
                <button
                  key={model.id}
                  onClick={() => {
                    onModelChange(model.id);
                    setIsOpen(false);
                  }}
                  className={`
                    w-full flex items-start gap-3 px-3 py-2 text-left hover:bg-gray-50 transition-colors
                    ${isSelected ? 'bg-blue-50 border-r-2 border-blue-500' : ''}
                  `}
                >
                  <IconComponent className={`w-5 h-5 mt-0.5 ${model.color}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`font-medium text-sm ${isSelected ? 'text-blue-700' : 'text-gray-900'}`}>
                        {model.name}
                      </span>
                      {isSelected && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5 leading-tight">
                      {model.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
          
          <div className="px-3 py-2 bg-gray-50 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Model can be changed between conversations
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMModelSelector;