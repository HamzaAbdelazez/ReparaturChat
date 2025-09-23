import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Plus } from "lucide-react";

// Components
import DocumentUpload from "../components/DocumentUpload";
import ToolAnalysis from "../components/ToolAnalysis";
import DeviceSelector from "../components/DeviceSelector";
import RepairAnalysis from "../components/RepairAnalysis";
import ChatInterface from "../components/ChatInterface";
import DeviceManager from "../components/DeviceManager";
import "../App.css";

function ReparaturApp() {
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
  const [chatMode, setChatMode] = useState("pdf"); // "pdf" or "general"
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
      setChatMode("pdf");
      
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
      const response = await fetch(`http://localhost:8000/conversations/${conversationId}/messages`);
      if (response.ok) {
        const messages = await response.json();
        setHistory(
          messages.map((msg) => ({
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
        setChatMode("pdf");
        
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
      // Use chat mode to determine endpoint
      const endpoint = (chatMode === "pdf" && uploadedPdf) ? `/chat/pdf` : `/chat/general`;
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

  // Load chat history
  useEffect(() => {
    if (!userId) return;

    async function loadHistory() {
      try {
        // Load all messages for user, optionally filtered by document
        const url = uploadedPdf 
          ? `http://localhost:8000/chat/history?user_id=${userId}&document_id=${uploadedPdf.id}`
          : `http://localhost:8000/chat/history?user_id=${userId}`;
          
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          setHistory(
            data.map((msg) => ({
              id: msg.id,
              type: msg.role,
              content: msg.message,
            }))
          );
        }
      } catch (err) {
        console.error("Failed to load chat history", err);
      }
    }

    loadHistory();
  }, [userId, uploadedPdf]);

  // Fetch tools
  useEffect(() => {
    if (!uploadedPdf) return;

    async function loadTools() {
      try {
        const res = await fetch(
          `http://localhost:8000/documents/${uploadedPdf.id}/tools`
        );
        if (res.ok) {
          const data = await res.json();
          setTools(data);
        }
      } catch (err) {
        console.error("Failed to load tools", err);
      }
    }

    loadTools();
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
      <div className="w-64 bg-gray-700 text-white flex flex-col p-4 h-screen sticky top-0">
        <button
          onClick={createNewConversation}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm font-semibold"
        >
          <Plus size={16} /> New Chat
        </button>

        <h2 className="mt-6 mb-2 text-sm font-bold uppercase tracking-wide text-gray-400">
          Conversations
        </h2>
        <div className="flex-1 overflow-y-auto space-y-2">
          {conversations.length === 0 ? (
            <p className="text-gray-500 text-sm italic">No conversations yet</p>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => switchToConversation(conv.id)}
                className={`p-2 rounded text-sm cursor-pointer hover:bg-gray-600 ${
                  currentConversationId === conv.id
                    ? "bg-blue-600"
                    : "bg-gray-600"
                }`}
              >
                <div className="font-medium truncate">{conv.title}</div>
                <div className="text-xs text-gray-300 mt-1 truncate">
                  {conv.latest_message}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {conv.message_count} messages
                </div>
              </div>
            ))
          )}
        </div>

        <button
          onClick={handleSignOut}
          className="mt-4 bg-red-500 hover:bg-red-600 px-3 py-2 rounded text-sm font-semibold"
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center overflow-y-auto">
        <div className="w-[80%] max-w-2xl py-6">
          {/* Header */}
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight">
            ReparaturApp,
          </h1>
          <br />
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight mb-4">
           Repair instead of replace.
          </h1>

          <p className="text-blue-600 leading-tight tracking-tight mb-4 text-lg">
            Upload a repair manual or ask a general question.
          </p>

          {/* Quick Suggestions */}
          <div className="flex w-full mb-6 gap-3 text-sm text-neutral-800">
            <div
              className="group relative grow border border-gray-300 shadow-sm hover:shadow-md hover:bg-neutral-100/30 rounded-xl p-4 transition-all duration-300 cursor-pointer"
              onClick={(e) => handleSend(e, "What does the repair cost compared to a professional?")}
            >
              What does the repair cost compared to a professional?
            </div>
            <div
              className="group relative grow border border-gray-300 shadow-sm hover:shadow-md hover:bg-neutral-100/30 rounded-xl p-4 transition-all duration-300 cursor-pointer"
              onClick={(e) => handleSend(e, "What tools do I need for the repair?")}
            >
              What tools do I need for the repair?
            </div>
          </div>

          {/* Traditional PDF Upload Interface */}
          <DocumentUpload
            file={file}
            uploadStatus={uploadStatus}
            uploadedPdf={uploadedPdf}
            onFileChange={handleFileChange}
            onUpload={handleUploadPdf}
            onDelete={handleDeletePdf}
            chatMode={chatMode}
            onChatModeChange={handleChatModeChange}
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

          <RepairAnalysis
            uploadedPdf={uploadedPdf}
            selectedDevice={selectedDevice}
            userId={userId}
            showAnalysis={showAnalysis}
            repairAnalysis={repairAnalysis}
            onPerformAnalysis={handleRepairAnalysis}
          />

          <ChatInterface
            question={question}
            onQuestionChange={setQuestion}
            history={history}
            onSend={handleSend}
            isLoading={isLoading}
            rating={rating}
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