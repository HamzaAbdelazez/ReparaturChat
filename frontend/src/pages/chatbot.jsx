import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

// Custom Hooks
import { useAuth } from "../hooks/useAuth";
import { useConversations } from "../hooks/useConversations";
import { usePdfUpload } from "../hooks/usePdfUpload";
import { useChat } from "../hooks/useChat";
import { useDevices } from "../hooks/useDevices";

// Components
import Sidebar from "../components/Sidebar";
import MainContent from "../components/MainContent";
import DeviceManager from "../components/DeviceManager";

// Utilities
import { handleRepairAnalysis } from "../utils/repairAnalysis";
import { clearConversationState } from "../utils/stateCleanup";

import "../App.css";

function ReparaturApp() {
  const { t } = useTranslation();

  // Custom Hooks
  const { userId, rating, isLoading: authLoading, isAuthenticated, handleSignOut } = useAuth();
  const {
    conversations,
    currentConversationId,
    searchQuery,
    setSearchQuery,
    setCurrentConversationId,
    loadConversations,
    createNewConversation,
    switchToConversation,
    deleteConversation,
    generateConversationTitle
  } = useConversations(userId);

  const {
    file,
    uploadedPdf,
    uploadStatus,
    tools,
    setUploadedPdf,
    setUploadStatus,
    setTools,
    handleFileChange,
    handleUploadPdf,
    handleDeletePdf,
    clearPdfState
  } = usePdfUpload(userId);

  const {
    question,
    setQuestion,
    history,
    setHistory,
    isLoading,
    handleSend,
    clearChatState,
    selectedModel,
    setSelectedModel
  } = useChat(userId, rating, uploadedPdf);

  const {
    userDevices,
    selectedDevice,
    showDeviceManager,
    setSelectedDevice,
    setShowDeviceManager,
    loadUserDevices
  } = useDevices();

  // Additional state for repair analysis
  const [repairAnalysis, setRepairAnalysis] = useState(null);
  const [showAnalysis, setShowAnalysis] = useState(false);

  // Load initial data when user is available
  useEffect(() => {
    if (userId) {
      // Reset conversation state on page refresh for clean start
      setHistory([]);
      setCurrentConversationId(null);
      setTools([]);
      setRepairAnalysis(null);
      setShowAnalysis(false);

      loadUserDevices(userId);
      loadConversations(userId);
    }
  }, [userId, loadUserDevices, loadConversations, setHistory, setCurrentConversationId, setTools]);

  // Enhanced Sign Out Handler
  const handleEnhancedSignOut = () => {
    // Clear all state before signing out
    clearChatState();
    clearPdfState();
    setSelectedDevice(null);
    setRepairAnalysis(null);
    setShowAnalysis(false);
    setShowDeviceManager(false);

    handleSignOut();
  };

  // Enhanced Create New Conversation
  const handleCreateNewConversation = async () => {
    const newConversationId = await createNewConversation();
    if (newConversationId) {
      // Clear conversation-specific state
      clearConversationState({
        setHistory,
        setRepairAnalysis,
        setShowAnalysis,
        clearPdfState
      });
      setCurrentConversationId(newConversationId);
    }
  };

  // Enhanced Switch Conversation
  const handleSwitchConversation = async (conversationId) => {
    // Clear previous conversation state
    setRepairAnalysis(null);
    setShowAnalysis(false);

    const { history: newHistory, pdfAttachment } = await switchToConversation(conversationId);
    setHistory(newHistory);

    // Handle PDF attachment
    if (pdfAttachment) {
      setUploadedPdf({
        id: pdfAttachment.id,
        title: pdfAttachment.title
      });
      setUploadStatus("uploaded");
    } else {
      // Clear PDF-related state if no PDF attachment
      clearPdfState();
    }
  };

  // Enhanced PDF Upload
  const handleEnhancedUploadPdf = async () => {
    const uploadedData = await handleUploadPdf(currentConversationId);
    if (uploadedData && currentConversationId) {
      loadConversations(userId); // Refresh conversations list
    }
  };

  // Enhanced Send Message
  const handleEnhancedSend = async (e, predefinedQuestion = null) => {
    const conversationId = await handleSend(
      e,
      predefinedQuestion,
      currentConversationId,
      createNewConversation,
      generateConversationTitle,
      loadConversations
    );

    if (conversationId && conversationId !== currentConversationId) {
      setCurrentConversationId(conversationId);
    }
  };

  // Handle repair analysis
  const handleRepairAnalysisAction = (analysisData) => {
    handleRepairAnalysis(analysisData, setRepairAnalysis, setShowAnalysis);
  };

  // Enhanced Delete Conversation
  const handleDeleteConversation = async (conversationId) => {
    const success = await deleteConversation(conversationId); // Calls hook

    if (success) {
      // Refresh conversations from backend
      await loadConversations(userId);

      // Clear current conversation if it was deleted
      if (currentConversationId === conversationId) {
        clearChatState();
        clearPdfState();
        setRepairAnalysis(null);
        setShowAnalysis(false);
        setCurrentConversationId(null);
      }
    } else {
      console.error("Failed to delete conversation");
    }

    return success;
  };


  // Show loading state while authentication is being checked
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen flex bg-neutral-100">
      {/* Sidebar */}
      <div className="flex-shrink-0 h-screen">
        <Sidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onCreateNew={handleCreateNewConversation}
          onSwitchConversation={handleSwitchConversation}
          onDeleteConversation={handleDeleteConversation}
          onSignOut={handleEnhancedSignOut}
        />
      </div>


      {/* Main Content */}
      <div className="flex-1 h-screen overflow-y-auto bg-neutral-100">
        <MainContent
          // PDF related
          file={file}
          uploadStatus={uploadStatus}
          uploadedPdf={uploadedPdf}
          onFileChange={handleFileChange}
          onUpload={handleEnhancedUploadPdf}
          onDelete={handleDeletePdf}
          tools={tools}

          // Chat related
          question={question}
          onQuestionChange={setQuestion}
          history={history}
          onSend={handleEnhancedSend}
          isLoading={isLoading}
          rating={rating}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}

          // Device related
          userDevices={userDevices}
          selectedDevice={selectedDevice}
          onDeviceSelect={setSelectedDevice}
          onManageDevices={() => setShowDeviceManager(true)}

          // Analysis related
          showAnalysis={showAnalysis}
          repairAnalysis={repairAnalysis}
          onPerformAnalysis={handleRepairAnalysisAction}

          // User
          userId={userId}
        />
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