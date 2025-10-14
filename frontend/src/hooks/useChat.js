import { useState, useCallback } from "react";

export const useChat = (userId, rating, uploadedPdf) => {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Send message
  const handleSend = useCallback(async (
    e, 
    predefinedQuestion = null,
    currentConversationId,
    createNewConversation,
    generateConversationTitle,
    loadConversations
  ) => {
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

    return conversationId;
  }, [question, userId, rating, uploadedPdf]);

  const clearChatState = useCallback(() => {
    setHistory([]);
    setQuestion("");
  }, []);

  return {
    question,
    setQuestion,
    history,
    setHistory,
    isLoading,
    handleSend,
    clearChatState
  };
};