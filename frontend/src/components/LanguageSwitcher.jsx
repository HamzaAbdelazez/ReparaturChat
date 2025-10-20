import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [currentLang, setCurrentLang] = useState('de'); // default Germany

  // Sync with i18n language on mount
  useEffect(() => {
    setCurrentLang(i18n.language);
  }, [i18n.language]);

  const toggleLanguage = () => {
    const newLang = currentLang === 'en' ? 'de' : 'en';
    i18n.changeLanguage(newLang);
    setCurrentLang(newLang);
  };

  return (
    <button
      onClick={toggleLanguage}
      className="px-3 py-2 rounded shadow hover:shadow-md transition-all duration-200"
    >
      {currentLang === 'en' ? (
        // USA flag SVG
        <svg width="24" height="16" viewBox="0 0 7410 3900" xmlns="http://www.w3.org/2000/svg">
          <g fillRule="evenodd">
            <path fill="#B22234" d="M0 0h7410v3900H0z"/>
            <path fill="#FFF" d="M0 300h7410v300H0zm0 600h7410v300H0zm0 600h7410v300H0zm0 600h7410v300H0zm0 600h7410v300H0zm0 600h7410v300H0z"/>
            <path fill="#3C3B6E" d="M0 0h2964v2100H0z"/>
            <g fill="#FFF">
              <g id="s">
                {Array.from({length:9}).map((_, row) =>
                  Array.from({length:6}).map((_, col) => {
                    const x = col * 494 + (row % 2 === 0 ? 0 : 247);
                    const y = row * 233;
                    return <path key={`${row}-${col}`} d={`M${x+123},${y+58} l30,0 l-15,26 z`}/>
                  })
                )}
              </g>
            </g>
          </g>
        </svg>
      ) : (
        // Germany flag SVG
        <svg width="24" height="16" viewBox="0 0 5 3" xmlns="http://www.w3.org/2000/svg">
          <rect width="5" height="1" y="0" fill="#000"/>
          <rect width="5" height="1" y="1" fill="#DD0000"/>
          <rect width="5" height="1" y="2" fill="#FFCE00"/>
        </svg>
      )}
    </button>
  );
}

export default LanguageSwitcher;
