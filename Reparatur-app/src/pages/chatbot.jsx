import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function ReparaturApp() {
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [uploadedPdf, setUploadedPdf] = useState(null);
  const [history, setHistory] = useState([]);
  const [userId, setUserId] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("not_uploaded");
  const [requirements, setRequirements] = useState(null);
  const [loadingReq, setLoadingReq] = useState(false);
  const navigate = useNavigate();

  // Load user from localStorage
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

  // Handle file input
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
      setUploadedPdf(null);
      setUploadStatus("not_uploaded");
      setRequirements(null);
    }
  };

  // Upload PDF
  const handleUploadPdf = async () => {
    if (!file) {
      alert("Please select a PDF file before uploading.");
      return;
    }

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
        const error = await response.json();
        console.error("Upload error:", error.detail);
        setUploadStatus("error");
        return;
      }

      const result = await response.json();
      setUploadedPdf(result);
      setUploadStatus("uploaded");

      // fetchRequirements(result.id);
    } catch (error) {
      console.error("Error uploading PDF:", error);
      setUploadStatus("error");
    }
  };

  // Fetch requirements
  // const fetchRequirements = async (docId) => {
  //   setLoadingReq(true);
  //   try {
  //     const res = await fetch(`http://localhost:8000/documents/${docId}/requirements`);
  //     if (!res.ok) throw new Error("Failed to load requirements");
  //     const data = await res.json();
  //     setRequirements(data);
  //   } catch (err) {
  //     console.error("Requirements error:", err);
  //     setRequirements(null);
  //   } finally {
  //     setLoadingReq(false);
  //   }
  // };

  // Send a question
  const handleSend = async (e) => {
    e.preventDefault();
    if (!question.trim()) {
      alert("Please enter a question!");
      return;
    }

    const newEntry = { type: "user", content: question };
    setHistory((prev) => [...prev, newEntry]);
    const currentQuestion = question;
    setQuestion("");

    try {
      let url;
      if (uploadedPdf) {
        url = `http://localhost:8000/chat/?question=${encodeURIComponent(
          currentQuestion
        )}&document_id=${uploadedPdf.id}&user_id=${userId}`;
      } else {
        url = `http://localhost:8000/chat/general?question=${encodeURIComponent(
          currentQuestion
        )}&user_id=${userId}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        const error = await response.json();
        console.error("Chat error:", error.detail);
        setHistory((prev) => [
          ...prev,
          { type: "bot", content: "❌ Failed to get answer." },
        ]);
        return;
      }

      const result = await response.json();
      setHistory((prev) => [...prev, { type: "bot", content: result.answer }]);
    } catch (error) {
      console.error("Error chatting:", error);
      setHistory((prev) => [
        ...prev,
        { type: "bot", content: "⚠️ Error connecting to backend." },
      ]);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center">
      {/* === Header === */}
      <div className="w-full bg-blue-500 text-white text-3xl font-bold text-center p-4 relative rounded-b-lg">
        🤖 Reparatur
        <button
          onClick={handleSignOut}
          className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
        >
          Logout
        </button>
      </div>

      {/* === Main Box === */}
      <div className="bg-white shadow-md rounded p-6 mt-8 w-full max-w-2xl text-center">
        <img
          src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png"
          alt="Robot"
          className="w-24 mx-auto mb-6"
        />

        {/* File Upload */}
        <div className="mb-6 text-left">
          <h2 className="text-xl font-semibold mb-4">📄 Upload PDF</h2>
          <div className="flex items-center justify-between space-x-2">
            <input type="file" accept="application/pdf" onChange={handleFileChange} />
            <button
              onClick={handleUploadPdf}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              disabled={uploadStatus === "uploading" || !file}
              
            >
              Upload
            </button>
          </div>
          <div className="mt-2 text-sm">
            {uploadStatus === "uploaded" && uploadedPdf && (
              <span className="text-green-600">✅ Uploaded: {uploadedPdf.title}</span>
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

        {/* Requirements */}
        {uploadedPdf && (
          <div className="mb-6 text-left border rounded-lg p-4 bg-gray-50">
            <h2 className="text-xl font-semibold mb-2">🔧 Tools & ⚙️ Parts</h2>
            {loadingReq ? (
              <p>⏳ Loading requirements...</p>
            ) : requirements ? (
              <div>
                <h3 className="font-medium">Tools:</h3>
                {requirements.tools?.length > 0 ? (
                  <ul className="list-disc list-inside mb-2">
                    {requirements.tools.map((tool, idx) => (
                      <li key={idx}>{tool}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No tools found</p>
                )}

                <h3 className="font-medium">Parts:</h3>
                {requirements.parts?.length > 0 ? (
                  <ul className="list-disc list-inside">
                    {requirements.parts.map((part, idx) => (
                      <li key={idx}>{part}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No parts found</p>
                )}
              </div>
            ) : (
              <p className="text-gray-500">No data available.</p>
            )}
          </div>
        )}

        {/* Chat Section */}
        <div className="text-left">
          <h2 className="text-xl font-semibold mb-4">🤖 Ask a Question</h2>
          <form onSubmit={handleSend} className="flex">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="How can I help you..."
              className="flex-1 border p-2 rounded-l focus:outline-none"
              required
            />
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 rounded-r"
            >
              Send
            </button>
          </form>
        </div>

        {/* Chat History */}
        <div className="mt-8 text-left max-h-60 overflow-y-auto border-t pt-4">
          <h3 className="text-lg font-semibold mb-2">🕘 History</h3>
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
      </div>
    </div>
  );
}

export default ReparaturApp;
