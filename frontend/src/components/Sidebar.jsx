import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Plus, Trash2, ChevronLeft, ChevronRight } from "lucide-react";
import ConfirmationModal from "./ConfirmationModal";

function Sidebar({
  conversations,
  currentConversationId,
  searchQuery,
  onSearchChange,
  onCreateNew,
  onSwitchConversation,
  onSignOut,
  onDeleteConversation
}) {
  const { t } = useTranslation();
  const [confirmModal, setConfirmModal] = useState({ isOpen: false, conversationId: null, title: "" });
  const [isOpen, setIsOpen] = useState(true); // Sidebar open/close

  const filteredConversations = conversations.filter(
    (conv) =>
      searchQuery === "" ||
      (conv.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (conv.latest_message && conv.latest_message.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleDeleteClick = (conversationId, title) => {
    setConfirmModal({ isOpen: true, conversationId, title });
  };

  const handleDeleteConfirm = async () => {
    try {
      const success = await onDeleteConversation(confirmModal.conversationId);
      if (!success) alert(t('conversations.deleteFailed'));
      return success; // <-- important
    } catch (err) {
      console.error(err);
      alert(t('conversations.deleteFailed'));
      return false;
    }
  };


  const toggleSidebar = () => setIsOpen(!isOpen);

  return (
    <div className={`flex flex-col bg-gray-700 text-white transition-all duration-300 h-screen ${isOpen ? "w-64" : "w-16"}`}>
      {/* Sidebar toggle button */}
      <div className="flex items-center justify-between p-2 border-b border-gray-600">
        {isOpen && <span className="font-semibold">{t('navigation.conversations')}</span>}
        <button onClick={toggleSidebar}>
          {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
        </button>
      </div>

      {/* New Chat button */}
      {isOpen && (
        <button
          onClick={onCreateNew}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm font-semibold m-2"
        >
          <Plus size={16} /> {t('navigation.newChat')}
        </button>
      )}

      {/* Search Conversations */}
      {isOpen && (
        <div className="mb-2 px-2">
          <input
            type="text"
            placeholder={t('navigation.searchConversations')}
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-2 py-1 text-sm bg-gray-600 text-white placeholder-gray-400 border border-gray-500 rounded focus:outline-none focus:border-blue-400"
          />
        </div>
      )}

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-1 space-y-1">
        {filteredConversations.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            {t('conversations.noConversations')}
          </div>
        ) : (
          filteredConversations.map((conv) => {
            const safeTitle = !conv.title || conv.title === "[object Object]" ? t('conversations.untitled') : conv.title;
            return (
              <div
                key={conv.id}
                className={`flex items-center justify-between p-2 rounded-lg transition-all duration-200 border text-sm h-20 overflow-hidden ${currentConversationId === conv.id
                  ? "bg-blue-600 border-blue-500"
                  : "bg-gray-600 border-gray-500 hover:bg-gray-550"
                  }`}
              >
                <div
                  className="flex-1 cursor-pointer overflow-hidden"
                  onClick={() => onSwitchConversation(conv.id)}
                >
                  <div className="font-medium truncate">{safeTitle}</div>
                  {conv.latest_message && (
                    <div className="text-xs text-gray-300 truncate">{conv.latest_message}</div>
                  )}
                  <div className="flex justify-between items-center text-xs text-gray-400 mt-1">
                    <span>{t('conversations.messages', { count: conv.message_count })}</span>
                  </div>
                </div>

                {/* Delete Button */}
                {isOpen && (
                  <button
                    onClick={() => handleDeleteClick(conv.id, safeTitle)}
                    className="ml-2 p-1 hover:bg-red-600 rounded transition-colors"
                    title={t('conversations.delete')}
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>



      {/* Logout */}
      {isOpen && (
        <button
          onClick={onSignOut}
          className="mt-2 bg-red-500 hover:bg-red-600 px-3 py-2 rounded text-sm font-semibold m-2"
        >
          {t('navigation.logout')}
        </button>
      )}

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, conversationId: null, title: "" })}
        onConfirm={handleDeleteConfirm}
        title={t('conversations.deleteTitle') || "Delete Conversation"}
        message={t('conversations.deleteConfirmation', { title: confirmModal.title })}
        confirmText={t('conversations.deleteButton') || "Delete"}
        cancelText={t('conversations.cancel') || "Cancel"}
        type="danger"
      />
    </div>
  );
}

export default Sidebar;
