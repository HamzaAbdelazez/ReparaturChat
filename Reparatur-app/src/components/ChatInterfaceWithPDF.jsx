import React, { useState, useRef } from "react";
import { Send, Paperclip, X, FileText } from "lucide-react";

function ChatInterfaceWithPDF({ 
  messages, 
  onSendMessage, 
  onUploadPDF, 
  isLoading,
  conversationId,
  userId
}) {
  const [message, setMessage] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (file) => {
    if (file && file.type === "application/pdf") {
      onUploadPDF(file);
    } else {
      alert("Please select a PDF file");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === "application/pdf");
    if (pdfFile) {
      handleFileSelect(pdfFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (msg, index) => {
    const isUser = msg.type === "user";
    const isPDF = msg.type === "pdf";
    
    return (
      <div key={index} className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isUser 
            ? "bg-blue-500 text-white" 
            : isPDF 
              ? "bg-gray-100 border border-gray-300" 
              : "bg-gray-200 text-gray-800"
        }`}>
          {isPDF ? (
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <div>
                <div className="font-medium text-sm">{msg.content}</div>
                {msg.attachment && (
                  <div className="text-xs text-gray-500 mt-1">
                    {msg.attachment.filename}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="whitespace-pre-wrap">{msg.content}</div>
          )}
          <div className={`text-xs mt-1 ${
            isUser ? "text-blue-100" : "text-gray-500"
          }`}>
            {formatTimestamp(msg.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-96 border rounded-lg bg-white">
      {/* Messages Area */}
      <div 
        className={`flex-1 overflow-y-auto p-4 ${
          isDragOver ? "bg-blue-50 border-2 border-dashed border-blue-300" : ""
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {isDragOver && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-blue-600">
              <FileText className="w-12 h-12 mx-auto mb-2" />
              <p className="font-medium">Drop PDF file here</p>
            </div>
          </div>
        )}
        
        {!isDragOver && messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="font-medium">Start a conversation or upload a PDF</p>
              <p className="text-sm mt-1">Drag & drop PDF files here or click the 📎 button</p>
            </div>
          </div>
        )}
        
        {!isDragOver && messages.map((msg, index) => renderMessage(msg, index))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-200 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex items-end gap-2">
          {/* PDF Upload Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="Upload PDF"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          
          {/* Message Input */}
          <div className="flex-1">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={1}
              style={{
                minHeight: '40px',
                maxHeight: '120px',
                height: 'auto'
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
          </div>
          
          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            className={`p-2 rounded-lg transition-colors ${
              message.trim() && !isLoading
                ? "bg-blue-500 text-white hover:bg-blue-600"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              handleFileSelect(file);
              e.target.value = ''; // Reset input
            }
          }}
          className="hidden"
        />
      </div>
    </div>
  );
}

export default ChatInterfaceWithPDF;