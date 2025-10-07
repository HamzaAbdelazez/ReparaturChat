import React from "react";
import { useTranslation } from "react-i18next";

function ChatInterface({ 
  history, 
  question, 
  rating,
  isLoading,
  onQuestionChange,
  onRatingChange, 
  onSend,
  onQuickSend 
}) {
  const { t } = useTranslation();
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (question.trim() && !isLoading) {
        onSend(e);
      }
    }
  };
  return (
    <>

      {/* Chat Box */}
      <div className="bg-white p-4 rounded-xl shadow-md max-h-60 overflow-y-auto mb-6">
        <h3 className="text-lg font-semibold mb-2">{t('chat.title')}</h3>
        {history.length === 0 ? (
          <p className="text-gray-500 italic">{t('chat.noMessages')}</p>
        ) : (
          <ul className="space-y-2">
            {history.map((msg, index) => (
              <li
                key={index}
                className={`p-2 rounded ${
                  msg.type === "user"
                    ? "bg-blue-100 text-right"
                    : "bg-gray-200 text-left"
                }`}
              >
                {msg.content}
              </li>
            ))}
            {isLoading && (
              <li className="p-2 rounded bg-gray-100 text-left">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <span className="text-gray-500 text-sm">{t('chat.aiThinking')}</span>
                </div>
              </li>
            )}
          </ul>
        )}
      </div>

      {/* Chat Input */}
      <form
        onSubmit={onSend}
        className="bg-white h-28 rounded-2xl shadow-md border border-neutral-200 relative"
      >
        <div className="flex">
          <textarea
            className="grow m-4 outline-none min-h-16 resize-none"
            placeholder={t('chat.placeholder')}
            value={question}
            onChange={(e) => onQuestionChange(e.target.value)}
            onKeyDown={handleKeyDown}
            maxLength={4000}
          />
        </div>
        <div className="flex gap-2 items-center absolute right-3 bottom-2">
          <div className="text-xs text-gray-500">
            {t('chat.characterCount', { count: question.length })}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className={`rounded-full text-white w-8 h-8 flex items-center justify-center ${
              isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-neutral-700 hover:bg-neutral-800'
            }`}
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </>
  );
}

export default ChatInterface;