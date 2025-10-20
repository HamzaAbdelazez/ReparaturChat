import React, { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import MarkdownRenderer from "./MarkdownRenderer";

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
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history, isLoading]);

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

      {/* Chat Box  */}
      <div className="bg-white p-6 rounded-xl shadow-md max-h-[800px] overflow-y-auto mb-6">
        <h3 className="text-xl font-semibold mb-4">{t('chat.title')}</h3>
        {history.length === 0 ? (
          <p className="text-gray-500 italic text-lg">{t('chat.noMessages')}</p>
        ) : (
          <ul className="space-y-4">
            {history.map((msg, index) => (
              <li
                key={index}
                className={`p-4 rounded-lg text-base leading-relaxed shadow-sm ${
                  msg.type === "user"
                    ? "bg-blue-100 text-right border-l-4 border-blue-500"
                    : "bg-gray-100 text-left border-l-4 border-gray-400"
                }`}
              >
                <div className={`font-medium text-sm mb-2 ${
                  msg.type === "user" ? "text-blue-600" : "text-gray-600"
                }`}>
                  {msg.type === "user" ? "You" : "Assistant"}
                </div>
                {msg.type === "user" ? (
                  <div className="whitespace-pre-wrap text-gray-800">{msg.content}</div>
                ) : (
                  <MarkdownRenderer 
                    content={msg.content} 
                    className="text-gray-800"
                  />
                )}
              </li>
            ))}
            {isLoading && (
              <li className="p-4 rounded-lg bg-gray-100 text-left border-l-4 border-gray-400 shadow-sm">
                <div className="font-medium text-sm mb-2 text-gray-600">Assistant</div>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <span className="text-gray-500 text-base">{t('chat.aiThinking')}</span>
                </div>
              </li>
            )}
            <div ref={chatEndRef} />
          </ul>
        )}
      </div>

      {/* Chat Input */}
      <form
        onSubmit={onSend}
        className="bg-white h-30rounded-2xl shadow-md border border-neutral-200 relative"
      >
        <div className="flex">
          <textarea
            className="grow m-4 outline-none min-h-24 resize-none"
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