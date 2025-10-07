import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Plus } from "lucide-react";

// Components
import DocumentUpload from "../components/DocumentUpload";
import ToolAnalysis from "../components/ToolAnalysis";
import DeviceSelector from "../components/DeviceSelector";
import RepairAnalysis from "../components/RepairAnalysis";
import ChatInterface from "../components/ChatInterface";
import DeviceManager from "../components/DeviceManager";
import LanguageSwitcher from "../components/LanguageSwitcher";
import "../App.css";

function ReparaturApp() {
  const { t } = useTranslation();
  
  // State
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [uploadedPdf, setUploadedPdf] = useState(null);
  const [history, setHistory] = useState([]);
  const [userId, setUserId] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("not_uploaded");
  const [tools, setTools] = useState([]);
  const [rating, setRating] = useState(1);
  const [userDevices, setUserDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [repairAnalysis, setRepairAnalysis] = useState(null);
  const [showDeviceManager, setShowDeviceManager] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  // Auto-detect chat mode based on PDF presence - no manual selection needed
  const navigate = useNavigate();

  // Load user and devices
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/");
      return;
    }
    try {
      const parsed = JSON.parse(storedUser);
      setUserId(parsed.id);
      
      // Initialize rating from user's skill level (default to 3 if not available)
      const userSkillLevel = parsed.skill_level || 3;
      setRating(userSkillLevel);
      
      // Reset conversation state on page refresh for clean start
      setHistory([]);
      setCurrentConversationId(null);
      setUploadedPdf(null);
      setFile(null);
      setUploadStatus("not_uploaded");
      setTools([]);
      setRepairAnalysis(null);
      setShowAnalysis(false);
      
      loadUserDevices(parsed.id);
      loadConversations(parsed.id);
    } catch {
      navigate("/");
    }
  }, [navigate]);

  // Load user devices
  const loadUserDevices = async (id) => {
    try {
      const response = await fetch(`http://localhost:8000/devices/user-devices/${id}`);
      if (response.ok) {
        const devices = await response.json();
        setUserDevices(devices);
      }
    } catch (error) {
      console.error("Error loading user devices:", error);
    }
  };

  // Load conversations
  const loadConversations = async (id) => {
    try {
      const response = await fetch(`http://localhost:8000/conversations/?user_id=${id}`);
      if (response.ok) {
        const conversations = await response.json();
        setConversations(conversations);
      }
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  };

  // Create new conversation
  const createNewConversation = async (title = null) => {
    if (!userId) return;
    
    // Generate a dynamic title based on timestamp if no title provided
    const conversationTitle = title || `Chat ${new Date().toLocaleString('en-US', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })}`;
    
    try {
      const response = await fetch(`http://localhost:8000/conversations/?user_id=${userId}&title=${encodeURIComponent(conversationTitle)}`, {
        method: "POST",
      });
      if (response.ok) {
        const newConversation = await response.json();
        setCurrentConversationId(newConversation.id);
        setHistory([]);
        
        // Clear conversation-specific state
        setRepairAnalysis(null);
        setShowAnalysis(false);
        setUploadedPdf(null);
        setUploadStatus("not_uploaded");
        setTools([]);
        setFile(null);
        
        loadConversations(userId);
        return newConversation.id;
      }
    } catch (error) {
      console.error("Error creating conversation:", error);
    }
    return null;
  };

  // Switch to conversation
  const switchToConversation = async (conversationId) => {
    try {
      setCurrentConversationId(conversationId);
      
      // Clear previous conversation state
      setRepairAnalysis(null);
      setShowAnalysis(false);
      
      const response = await fetch(`http://localhost:8000/conversations/${conversationId}/messages`);
      if (response.ok) {
        const messages = await response.json();
        
        // Filter out system messages from chat display (but keep them for PDF attachment detection)
        const chatMessages = messages.filter(msg => msg.type !== 'system');
        
        setHistory(
          chatMessages.map((msg) => ({
            id: msg.id,
            type: msg.type,
            content: msg.content,
            timestamp: msg.timestamp,
            attachment: msg.attachment || null
          }))
        );
        
        // If there's a PDF attachment, set it as uploaded PDF
        const pdfMessage = messages.find(msg => msg.attachment && msg.attachment.type === 'pdf');
        if (pdfMessage) {
          setUploadedPdf({
            id: pdfMessage.attachment.id,
            title: pdfMessage.attachment.filename
          });
          setUploadStatus("uploaded");
          
          // Load tools for this PDF
          loadToolsForPdf(pdfMessage.attachment.id);
        } else {
          // Clear PDF-related state if no PDF attachment
          setUploadedPdf(null);
          setUploadStatus("not_uploaded");
          setTools([]);
        }
      }
    } catch (error) {
      console.error("Error loading conversation messages:", error);
    }
  };

  // Delete PDF
  const handleDeletePdf = async () => {
    if (!uploadedPdf || !userId) return;
    
    if (!window.confirm(`Are you sure you want to delete "${uploadedPdf.title}"?`)) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/uploadedPdfs/${uploadedPdf.id}?user_id=${userId}`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        // Clear PDF-related state
        setUploadedPdf(null);
        setFile(null);
        setUploadStatus("not_uploaded");
        setTools([]);
        setRepairAnalysis(null);
        setShowAnalysis(false);
        
        console.log("PDF deleted successfully");
      } else {
        console.error("Failed to delete PDF");
      }
    } catch (error) {
      console.error("Error deleting PDF:", error);
    }
  };

  // Chat Mode Change
  const handleChatModeChange = (mode) => {
    setChatMode(mode);
  };


  // File Change
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setUploadedPdf(null);
      setUploadStatus("not_uploaded");
    }
  };

  // Upload PDF
  const handleUploadPdf = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploadStatus("uploading");
      const response = await fetch(
        `http://localhost:8000/uploadedPdfs/?user_id=${userId}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        const data = await response.json();
        setUploadedPdf(data);
        setUploadStatus("uploaded");
        
        // Load tools immediately after successful upload
        loadToolsForPdf(data.id);
        
        // If we have a current conversation, save the PDF attachment (only once)
        if (currentConversationId) {
          try {
            // Check if this PDF is already attached to avoid duplicates
            const existingMessages = await fetch(`http://localhost:8000/conversations/${currentConversationId}/messages`);
            if (existingMessages.ok) {
              const messages = await existingMessages.json();
              const pdfAlreadyAttached = messages.some(msg => 
                msg.attachment && 
                msg.attachment.type === 'pdf' && 
                msg.attachment.id === data.id
              );
              
              if (!pdfAlreadyAttached) {
                await fetch(`http://localhost:8000/conversations/${currentConversationId}/messages`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    message_type: "system",
                    content: `PDF uploaded: ${data.title}`,
                    attachment: {
                      type: "pdf",
                      id: data.id,
                      filename: data.title
                    }
                  })
                });
              }
            }
            loadConversations(userId); // Refresh conversations list
          } catch (error) {
            console.error("Failed to save PDF attachment to conversation:", error);
          }
        }
      } else {
        setUploadStatus("error");
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("error");
    }
  };

  // Generate conversation title from message
  const generateConversationTitle = (message) => {
    // Clean the message and truncate if too long
    let title = message.trim();
    
    // Remove common prefixes
    title = title.replace(/^(can you|how|what|where|when|why)\s+/i, '');
    
    // Truncate to reasonable length
    if (title.length > 40) {
      title = title.substring(0, 37) + '...';
    }
    
    // Capitalize first letter
    title = title.charAt(0).toUpperCase() + title.slice(1);
    
    return title || `Chat ${new Date().toLocaleString('en-US', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })}`;
  };

  // Send message
  const handleSend = async (e, predefinedQuestion = null) => {
    e.preventDefault();
    const messageText = predefinedQuestion || question;
    if (!messageText.trim()) return;

    let conversationId = currentConversationId;

    // Create conversation if none exists
    if (!conversationId) {
      try {
        // Generate a meaningful title from the first message
        const conversationTitle = generateConversationTitle(messageText);
        const response = await fetch(`http://localhost:8000/conversations/?user_id=${userId}&title=${encodeURIComponent(conversationTitle)}`, {
          method: "POST",
        });
        if (response.ok) {
          const newConversation = await response.json();
          conversationId = newConversation.id;
          setCurrentConversationId(conversationId);
          loadConversations(userId);
        } else {
          console.error("Failed to create conversation");
          return;
        }
      } catch (error) {
        console.error("Error creating conversation:", error);
        return;
      }
    }

    const userMessage = { type: "user", content: messageText };
    setHistory((prev) => [...prev, userMessage]);

    if (!predefinedQuestion) setQuestion("");
    setIsLoading(true);

    try {
      // Save user message to conversation
      await fetch(`http://localhost:8000/conversations/${conversationId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message_type: "user",
          content: messageText
        })
      });

      // Get AI response
      // Automatically detect endpoint based on PDF presence
      const endpoint = uploadedPdf ? `/chat/pdf` : `/chat/general`;
      const params = new URLSearchParams({
        question: messageText,
        user_id: userId,
        user_level_rate: rating,
        ...(conversationId && { conversation_id: conversationId }),
        ...(uploadedPdf && { document_id: uploadedPdf.id }),
      });

      const response = await fetch(`http://localhost:8000${endpoint}?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        const assistantMessage = { type: "assistant", content: data.answer };
        setHistory((prev) => [...prev, assistantMessage]);

        // Save assistant message to conversation
        await fetch(`http://localhost:8000/conversations/${conversationId}/messages`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message_type: "assistant",
            content: data.answer
          })
        });

        // Refresh conversations list
        loadConversations(userId);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Load chat history - Only for current conversation
  // This is handled by switchToConversation when a conversation is selected
  // We don't need to load all history automatically

  // Function to load tools for a specific PDF
  const loadToolsForPdf = async (pdfId) => {
    try {
      const res = await fetch(
        `http://localhost:8000/documents/${pdfId}/tools`
      );
      if (res.ok) {
        const data = await res.json();
        setTools(data);
      } else {
        console.error("Failed to load tools - response not ok:", res.status);
        setTools([]);
      }
    } catch (err) {
      console.error("Failed to load tools", err);
      setTools([]);
    }
  };

  // Fetch tools when uploadedPdf changes
  useEffect(() => {
    if (!uploadedPdf) {
      setTools([]);
      return;
    }
    loadToolsForPdf(uploadedPdf.id);
  }, [uploadedPdf]);

  // Handle repair analysis
  const handleRepairAnalysis = (analysisData) => {
    if (typeof analysisData === 'boolean') {
      setShowAnalysis(analysisData);
    } else {
      setRepairAnalysis(analysisData);
      setShowAnalysis(true);
    }
  };

  // Logout
  const handleSignOut = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="min-h-screen flex bg-neutral-100">
      {/* Sidebar */}
      <div className="w-64 md:w-64 sm:w-48 bg-gray-700 text-white flex flex-col p-4 h-screen sticky top-0 overflow-hidden">
        <button
          onClick={createNewConversation}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm font-semibold mb-4"
        >
          <Plus size={16} /> {t('navigation.newChat')}
        </button>

        {/* Search Conversations */}
        <div className="mb-4">
          <input
            type="text"
            placeholder={t('navigation.searchConversations')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-gray-600 text-white placeholder-gray-400 border border-gray-500 rounded focus:outline-none focus:border-blue-400"
          />
        </div>

        <h2 className="mb-2 text-sm font-bold uppercase tracking-wide text-gray-400">
          {t('navigation.conversations')} ({conversations.filter(conv => 
            conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (conv.latest_message && conv.latest_message.toLowerCase().includes(searchQuery.toLowerCase()))
          ).length})
        </h2>
        
        <div className="flex-1 overflow-y-auto space-y-2">
          {conversations.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500 text-sm">{t('conversations.noConversations')}</div>
              <div className="text-xs text-gray-400 mt-1">{t('conversations.noConversationsDescription')}</div>
            </div>
          ) : (
            conversations
              .filter(conv => 
                searchQuery === "" || 
                conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (conv.latest_message && conv.latest_message.toLowerCase().includes(searchQuery.toLowerCase()))
              )
              .map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => switchToConversation(conv.id)}
                  className={`p-3 rounded-lg text-sm cursor-pointer transition-all duration-200 border ${
                    currentConversationId === conv.id
                      ? "bg-blue-600 border-blue-500"
                      : "bg-gray-600 border-gray-500 hover:bg-gray-550"
                  }`}
                >
                  <div className="font-medium truncate">{conv.title}</div>
                  {conv.latest_message && (
                    <div className="text-xs text-gray-300 mt-1 truncate">
                      {conv.latest_message}
                    </div>
                  )}
                  <div className="flex justify-between items-center text-xs text-gray-400 mt-2">
                    <span>{t('conversations.messages', { count: conv.message_count })}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      conv.latest_message ? "bg-green-600" : "bg-gray-500"
                    }`}>
                      {conv.latest_message ? t('conversations.active') : t('conversations.new')}
                    </span>
                  </div>
                </div>
              ))
          )}
          
          {searchQuery && conversations.filter(conv => 
            conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (conv.latest_message && conv.latest_message.toLowerCase().includes(searchQuery.toLowerCase()))
          ).length === 0 && (
            <div className="text-center py-4 text-gray-400 text-sm">
              {t('conversations.noSearchResults', { query: searchQuery })}
            </div>
          )}
        </div>

        <div className="mb-3">
          <LanguageSwitcher />
        </div>

        <button
          onClick={handleSignOut}
          className="mt-2 bg-red-500 hover:bg-red-600 px-3 py-2 rounded text-sm font-semibold"
        >
          {t('navigation.logout')}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center overflow-y-auto">
        <div className="w-full max-w-4xl px-4 md:px-6 py-6">
          {/* Header */}
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight">
            {t('app.title')},
          </h1>
          <br />
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight mb-4">
           {t('app.subtitle')}
          </h1>


          {/* Quick Action Buttons */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">{t('quickActions.title')}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
              <button
                onClick={(e) => handleSend(e, t('quickActions.toolsQuestion'))}
                className="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 text-blue-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>🛠️</span>
                <span>{t('quickActions.requiredTools')}</span>
              </button>
              <button
                onClick={(e) => handleSend(e, t('quickActions.timeQuestion'))}
                className="bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-3 text-green-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>⏱️</span>
                <span>{t('quickActions.timeEstimate')}</span>
              </button>
              <button
                onClick={(e) => handleSend(e, t('quickActions.costQuestion'))}
                className="bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg p-3 text-purple-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>💰</span>
                <span>{t('quickActions.costComparison')}</span>
              </button>
              <button
                onClick={(e) => handleSend(e, t('quickActions.difficultyQuestion'))}
                className="bg-orange-50 hover:bg-orange-100 border border-orange-200 rounded-lg p-3 text-orange-700 transition-colors duration-200 flex items-center gap-2"
              >
                <span>📊</span>
                <span>{t('quickActions.difficultyCheck')}</span>
              </button>
            </div>
            
            {/* Contextual suggestions based on PDF upload */}
            {!uploadedPdf && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-600 text-center">
                  {t('tips.general')}
                </p>
              </div>
            )}
            
            {uploadedPdf && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-700 text-center">
                  {t('tips.pdfMode', { title: uploadedPdf.title })}
                </p>
              </div>
            )}
          </div>

          {/* Traditional PDF Upload Interface */}
          <DocumentUpload
            file={file}
            uploadStatus={uploadStatus}
            uploadedPdf={uploadedPdf}
            onFileChange={handleFileChange}
            onUpload={handleUploadPdf}
            onDelete={handleDeletePdf}
          />

          <ToolAnalysis
            tools={tools}
            userId={userId}
          />

          <DeviceSelector
            userDevices={userDevices}
            selectedDevice={selectedDevice}
            onDeviceSelect={setSelectedDevice}
            onManageDevices={() => setShowDeviceManager(true)}
          />

          <ChatInterface
            question={question}
            onQuestionChange={setQuestion}
            history={history}
            onSend={handleSend}
            isLoading={isLoading}
            rating={rating}
          />

          <RepairAnalysis
            uploadedPdf={uploadedPdf}
            selectedDevice={selectedDevice}
            userId={userId}
            showAnalysis={showAnalysis}
            repairAnalysis={repairAnalysis}
            onPerformAnalysis={handleRepairAnalysis}
            chatHistory={history}
          />
        </div>
      </div>

      {/* Device Manager Modal */}
      {showDeviceManager && (
        <DeviceManager
          userId={userId}
          onDeviceAdded={() => {
            loadUserDevices(userId);
            setShowDeviceManager(false);
          }}
          onClose={() => setShowDeviceManager(false)}
        />
      )}
    </div>
  );
}

export default ReparaturApp;