import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Wrench, Plus } from "lucide-react";
import "../App.css";

function ReparaturApp() {
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [uploadedPdf, setUploadedPdf] = useState(null);
  const [history, setHistory] = useState([]);
  const [allChats, setAllChats] = useState([]);
  const [userId, setUserId] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("not_uploaded");
  const navigate = useNavigate();

  // Load user
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/");
      return;
    }
    try {
      const parsed = JSON.parse(storedUser);
      setUserId(parsed.id);
    } catch {
      navigate("/");
    }
  }, [navigate]);

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
      if (!response.ok) {
        setUploadStatus("error");
        return;
      }
      const result = await response.json();
      setUploadedPdf(result);
      setUploadStatus("uploaded");
    } catch {
      setUploadStatus("error");
    }
  };

  // Send Question
  const handleSend = async (e, customQuestion = null) => {
    if (e) e.preventDefault();
    const finalQuestion = customQuestion || question;
    if (!finalQuestion.trim()) return;

    const newEntry = { type: "user", content: finalQuestion };
    setHistory((prev) => [...prev, newEntry]);
    setQuestion("");

    try {
      let url;
      if (uploadedPdf) {
        url = `http://localhost:8000/chat/?question=${encodeURIComponent(
          finalQuestion
        )}&document_id=${uploadedPdf.id}&user_id=${userId}`;
      } else {
        url = `http://localhost:8000/chat/general?question=${encodeURIComponent(
          finalQuestion
        )}&user_id=${userId}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        setHistory((prev) => [
          ...prev,
          { type: "bot", content: "❌ Failed to get answer." },
        ]);
        return;
      }

      const result = await response.json();
      setHistory((prev) => [...prev, { type: "bot", content: result.answer }]);
    } catch {
      setHistory((prev) => [
        ...prev,
        { type: "bot", content: "⚠️ Error connecting to backend." },
      ]);
    }
  };

  // Logout
  const handleSignOut = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="w-screen h-screen flex bg-neutral-100">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white flex flex-col p-4">
        <button
          onClick={() => {
            if (history.length > 0) setAllChats((p) => [...p, history]);
            setHistory([]);
          }}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm font-semibold"
        >
          <Plus size={16} /> New Chat
        </button>

        <h2 className="mt-6 mb-2 text-sm font-bold uppercase tracking-wide text-gray-400">
          Chat History
        </h2>
        <div className="flex-1 overflow-y-auto space-y-2">
          {allChats.length === 0 ? (
            <p className="text-gray-500 text-sm italic">No past chats</p>
          ) : (
            allChats.map((chat, idx) => (
              <div
                key={idx}
                className="p-2 rounded bg-gray-800 text-sm cursor-pointer hover:bg-gray-700"
                onClick={() => setHistory(chat)}
              >
                {chat[0]?.content.slice(0, 20) || "Conversation"}
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
      <div className="flex-1 flex flex-col items-center overflow-hidden">
        <div className="w-[80%] max-w-2xl py-6">
          {/* Header */}
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight">
            Hello there,
          </h1>
          <br />
          <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight mb-4">
            How can I help you?
          </h1>

          <p className="text-blue-600 leading-tight tracking-tight mb-6 text-lg">
            Upload a repair manual PDF or ask a general question.
          </p>

          {/* Quick Suggestions */}
          <div className="flex w-full mb-6 gap-3 text-sm text-neutral-800">
            <div
              className="group relative grow border border-gray-300 shadow-sm hover:shadow-md hover:bg-neutral-100/30 rounded-xl p-4 transition-all duration-300 cursor-pointer"
              onClick={(e) => handleSend(e, "How do I replace the filter?")}
            >
              How do I replace the filter?
            </div>
            <div
              className="group relative grow border border-gray-300 shadow-sm hover:shadow-md hover:bg-neutral-100/30 rounded-xl p-4 transition-all duration-300 cursor-pointer"
              onClick={(e) => handleSend(e, "What tools do I need for repair?")}
            >
              What tools do I need for repair?
            </div>
          </div>

          {/* Upload Box */}
          <div className="mb-6">
            <label className="custum-file-upload">
              <div className="icon">
                <Wrench className="w-12 h-12 text-blue-600" />
              </div>
              <div className="text">
                <span>{file ? file.name : "Click to upload your PDF"}</span>
              </div>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
              />
            </label>

            <div className="mt-3 flex justify-center">
              <button
                onClick={handleUploadPdf}
                disabled={uploadStatus === "uploading" || !file}
                className={`bg-blue-500 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded ${
                  uploadStatus === "uploading" || !file
                    ? "opacity-50 cursor-not-allowed"
                    : ""
                }`}
              >
                {uploadStatus === "uploading" ? "Uploading..." : "Upload"}
              </button>
            </div>

            <div className="mt-2 text-sm text-center">
              {uploadStatus === "uploaded" && uploadedPdf && (
                <span className="text-green-600">
                  ✅ Uploaded: {uploadedPdf.title}
                </span>
              )}
              {uploadStatus === "uploading" && (
                <span className="text-blue-600">⏳ Uploading...</span>
              )}
              {uploadStatus === "error" && (
                <span className="text-red-600">❌ Upload failed</span>
              )}
              {uploadStatus === "not_uploaded" && file && (
                <span className="text-gray-600">⚠️ Not uploaded yet</span>
              )}
            </div>
          </div>

          {/* Chat History (on top) */}
          <div className="bg-white p-4 rounded-xl shadow-md max-h-60 overflow-y-auto mb-6">
            <h3 className="text-lg font-semibold mb-2">History</h3>
            {history.length === 0 ? (
              <p className="text-gray-500 italic">No messages yet.</p>
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
              </ul>
            )}
          </div>

          {/* Chat Input */}
          <form
            onSubmit={handleSend}
            className="bg-white h-28 rounded-2xl shadow-md border border-neutral-200 relative"
          >
            <div className="flex">
              <textarea
                className="grow m-4 outline-none min-h-16 resize-none"
                placeholder="Type your question here ..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                maxLength={4000}
              />
            </div>
            <div className="flex gap-2 items-center absolute right-3 bottom-2">
              <div className="text-xs text-gray-500">
                {question.length}/4000
              </div>
              <button
                type="submit"
                className="bg-neutral-700 rounded-full text-white w-8 h-8 flex items-center justify-center"
              >
                ➤
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ReparaturApp;
