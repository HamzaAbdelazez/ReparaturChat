import React from 'react';
import { useTranslation } from 'react-i18next';
import { Languages } from 'lucide-react';

function LanguageSwitcher() {
  const { i18n, t } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="relative group">
      <button className="flex items-center gap-2 bg-gray-600 hover:bg-gray-550 px-3 py-2 rounded text-sm font-medium transition-colors">
        <Languages size={16} />
        <span>{t('language.switch')}</span>
      </button>
      
      <div className="absolute right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <button
          onClick={() => changeLanguage('en')}
          className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors ${
            i18n.language === 'en' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
          }`}
        >
          🇺🇸 {t('language.english')}
        </button>
        <button
          onClick={() => changeLanguage('de')}
          className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors ${
            i18n.language === 'de' ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
          }`}
        >
          🇩🇪 {t('language.german')}
        </button>
      </div>
    </div>
  );
}

export default LanguageSwitcher;