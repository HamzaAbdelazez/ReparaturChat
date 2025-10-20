import { useState, useCallback } from "react";

export const useConversations = (userId) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Load conversations
  const loadConversations = useCallback(async (id) => {
    if (!id) return;
    try {
      const response = await fetch(`http://localhost:8000/conversations/?user_id=${id}`);
      if (response.ok) {
        const conversations = await response.json();
        setConversations(conversations);
      }
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  }, []);

  // Create new conversation
  const createNewConversation = useCallback(async (title = null) => {
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

        loadConversations(userId);
        return newConversation.id;
      }
    } catch (error) {
      console.error("Error creating conversation:", error);
    }
    return null;
  }, [userId, loadConversations]);

  // Switch to conversation
  const switchToConversation = useCallback(async (conversationId) => {
    try {
      setCurrentConversationId(conversationId);

      const response = await fetch(`http://localhost:8000/conversations/${conversationId}/messages`);
      if (response.ok) {
        const messages = await response.json();

        // Filter out system messages from chat display
        const chatMessages = messages.filter(msg => msg.type !== 'system');

        const history = chatMessages.map((msg) => ({
          id: msg.id,
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp,
          attachment: msg.attachment || null
        }));

        // Return both history and PDF attachment info
        const pdfMessage = messages.find(msg => msg.attachment && msg.attachment.type === 'pdf');
        return {
          history,
          pdfAttachment: pdfMessage ? {
            id: pdfMessage.attachment.id,
            title: pdfMessage.attachment.filename
          } : null
        };
      }
    } catch (error) {
      console.error("Error loading conversation messages:", error);
    }
    return { history: [], pdfAttachment: null };
  }, []);

  // Delete conversation
  const deleteConversation = useCallback(async (conversationId) => {
    if (!userId) return false;

    try {
      const response = await fetch(`http://localhost:8000/conversations/${conversationId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        // Remove from local state
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));

        // Clear current conversation if needed
        if (currentConversationId === conversationId) {
          setCurrentConversationId(null);
        }

        return true;
      } else {
        console.error("Failed to delete conversation");
        return false;
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
      return false;
    }
  }, [userId, currentConversationId]);


  // Generate conversation title from message
  const generateConversationTitle = useCallback((message) => {
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
  }, []);

  return {
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
  };
};