// import React, { useState, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { Wrench, Plus } from "lucide-react";
// import DeviceManager from "../components/DeviceManager";
// import "../App.css";

// function ReparaturApp() {
//   const [question, setQuestion] = useState("");
//   const [file, setFile] = useState(null);
//   const [uploadedPdf, setUploadedPdf] = useState(null);
//   const [history, setHistory] = useState([]);
//   const [userId, setUserId] = useState(null);
//   const [uploadStatus, setUploadStatus] = useState("not_uploaded");
//   const [tools, setTools] = useState([]); 
//   const [rating, setRating] = useState(1); 
//   const [userDevices, setUserDevices] = useState([]);
//   const [selectedDevice, setSelectedDevice] = useState(null);
//   const [repairAnalysis, setRepairAnalysis] = useState(null);
//   const [showDeviceManager, setShowDeviceManager] = useState(false);
//   const [showAnalysis, setShowAnalysis] = useState(false);
//   const navigate = useNavigate();

//   // Load user and devices
//   useEffect(() => {
//     const storedUser = localStorage.getItem("user");
//     if (!storedUser) {
//       navigate("/");
//       return;
//     }
//     try {
//       const parsed = JSON.parse(storedUser);
//       setUserId(parsed.id);
//       loadUserDevices(parsed.id);
//     } catch {
//       navigate("/");
//     }
//   }, [navigate]);

//   // Load user devices
//   const loadUserDevices = async (id) => {
//     try {
//       const response = await fetch(`http://localhost:8000/devices/user-devices/${id}`);
//       if (response.ok) {
//         const devices = await response.json();
//         setUserDevices(devices);
//       }
//     } catch (error) {
//       console.error("Error loading user devices:", error);
//     }
//   };

//   // File Change
//   const handleFileChange = (e) => {
//     if (e.target.files) {
//       setFile(e.target.files[0]);
//       setUploadedPdf(null);
//       setUploadStatus("not_uploaded");
//     }
//   };

//   // Upload PDF
//   const handleUploadPdf = async () => {
//     if (!file) return;
//     const formData = new FormData();
//     formData.append("file", file);

//     try {
//       setUploadStatus("uploading");
//       const response = await fetch(
//         `http://localhost:8000/uploadedPdfs/?user_id=${userId}`,
//         {
//           method: "POST",
//           body: formData,
//         }
//       );
//       if (!response.ok) {
//         setUploadStatus("error");
//         return;
//       }
//       const result = await response.json();
//       setUploadedPdf(result);
//       setUploadStatus("uploaded");

//       // 🔥 Fetch tools right after upload
//       const toolsRes = await fetch(
//         `http://localhost:8000/document_tools/?document_id=${result.id}`
//       );
//       if (toolsRes.ok) {
//         const toolsData = await toolsRes.json();
//         setTools(toolsData);
//       }
//     } catch {
//       setUploadStatus("error");
//     }
//   };

//   // Send Question
//   const handleSend = async (e, customQuestion = null) => {
//     if (e) e.preventDefault();
//     const finalQuestion = customQuestion || question;
//     if (!finalQuestion.trim()) return;

//     const newEntry = { type: "user", content: finalQuestion };
//     setHistory((prev) => [...prev, newEntry]);
//     setQuestion("");

//     try {
//       let url;
//       if (uploadedPdf) {
//         url = `http://localhost:8000/chat/?question=${encodeURIComponent(
//           finalQuestion
//         )}&document_id=${uploadedPdf.id}&user_id=${userId}&user_level_rate=${rating}`;
//       } else {
//         url = `http://localhost:8000/chat/general?question=${encodeURIComponent(
//           finalQuestion
//         )}&user_id=${userId}&user_level_rate=${rating}`;
//       }

//       const response = await fetch(url);
//       if (!response.ok) {
//         setHistory((prev) => [
//           ...prev,
//           { type: "bot", content: "❌ Failed to get answer." },
//         ]);
//         return;
//       }

//       const result = await response.json();
//       setHistory((prev) => [...prev, { type: "bot", content: result.answer }]);
//     } catch {
//       setHistory((prev) => [
//         ...prev,
//         { type: "bot", content: "⚠️ Error connecting to backend." },
//       ]);
//     }
//   };

//   // Fetch chat history
//   useEffect(() => {
//     if (!userId) return;

//     async function loadHistory() {
//       try {
//         let url = `http://localhost:8000/chat/history?user_id=${userId}`;
//         if (uploadedPdf) {
//           url += `&document_id=${uploadedPdf.id}`;
//         }
//         const res = await fetch(url);
//         if (res.ok) {
//           const data = await res.json();
//           setHistory(
//             data.map((msg) => ({
//               id: msg.id,
//               type: msg.role,
//               content: msg.message,
//             }))
//           );
//         }
//       } catch (err) {
//         console.error("Failed to load chat history", err);
//       }
//     }

//     loadHistory();
//   }, [userId, uploadedPdf]);

//   // Fetch tools (when switching docs)
//   useEffect(() => {
//     if (!uploadedPdf) return;

//     async function loadTools() {
//       try {
//         const res = await fetch(
//           `http://localhost:8000/document_tools/?document_id=${uploadedPdf.id}`
//         );
//         if (res.ok) {
//           const data = await res.json();
//           setTools(data);
//         }
//       } catch (err) {
//         console.error("Failed to load tools", err);
//       }
//     }

//     loadTools();
//   }, [uploadedPdf]);

//   // Repair Analysis Functions
//   const performRepairAnalysis = async () => {
//     if (!uploadedPdf || !selectedDevice) {
//       alert("Please upload a document and select a device first.");
//       return;
//     }

//     try {
//       setShowAnalysis(true);
      
//       // Fetch repair feasibility
//       const feasibilityResponse = await fetch(
//         `http://localhost:8000/repair-analysis/feasibility?user_id=${userId}&device_id=${selectedDevice.device_id}&document_id=${uploadedPdf.id}`
//       );
//       const feasibility = feasibilityResponse.ok ? await feasibilityResponse.json() : null;

//       // Fetch cost estimation
//       const costResponse = await fetch(
//         `http://localhost:8000/repair-analysis/cost-estimation?user_id=${userId}&document_id=${uploadedPdf.id}`
//       );
//       const costs = costResponse.ok ? await costResponse.json() : null;

//       // Fetch time estimation
//       const timeResponse = await fetch(
//         `http://localhost:8000/repair-analysis/time-estimation?user_id=${userId}&document_id=${uploadedPdf.id}`
//       );
//       const time = timeResponse.ok ? await timeResponse.json() : null;

//       // Fetch comparison
//       const comparisonResponse = await fetch(
//         `http://localhost:8000/repair-analysis/compare-options?user_id=${userId}&device_id=${selectedDevice.device_id}&document_id=${uploadedPdf.id}`
//       );
//       const comparison = comparisonResponse.ok ? await comparisonResponse.json() : null;

//       setRepairAnalysis({
//         feasibility,
//         costs,
//         time,
//         comparison
//       });
//     } catch (error) {
//       console.error("Error performing repair analysis:", error);
//       alert("Failed to perform repair analysis");
//     }
//   };

//   const checkWarranty = async (userDeviceId) => {
//     try {
//       const response = await fetch(`http://localhost:8000/devices/warranty-check/${userDeviceId}`);
//       if (response.ok) {
//         const warranty = await response.json();
//         alert(`Warranty Status: ${warranty.warranty_status}\n${
//           warranty.is_under_warranty 
//             ? `Valid until: ${new Date(warranty.warranty_expires_at).toLocaleDateString()}\nDays remaining: ${warranty.days_remaining}`
//             : "Warranty has expired"
//         }`);
//       }
//     } catch (error) {
//       console.error("Error checking warranty:", error);
//       alert("Failed to check warranty");
//     }
//   };

//   // Logout
//   const handleSignOut = () => {
//     localStorage.removeItem("user");
//     navigate("/");
//   };

//   return (
//     <div className="min-h-screen flex bg-neutral-100">
//       {/* Sidebar */}
//       <div className="w-64 bg-gray-700 text-white flex flex-col p-4 h-screen sticky top-0">
//         <button
//           onClick={() => setHistory([])}
//           className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded text-sm font-semibold"
//         >
//           <Plus size={16} /> New Chat
//         </button>

//         <h2 className="mt-6 mb-2 text-sm font-bold uppercase tracking-wide text-gray-400">
//           Chat History
//         </h2>
//         <div className="flex-1 overflow-y-auto space-y-2">
//           {history.length === 0 ? (
//             <p className="text-gray-500 text-sm italic">No messages yet</p>
//           ) : (
//             history.map((msg, idx) => (
//               <div
//                 key={msg.id || idx}
//                 className={`p-2 rounded text-sm cursor-pointer ${
//                   msg.type === "user"
//                     ? "bg-blue-500 text-right"
//                     : "bg-gray-400 text-left"
//                 }`}
//               >
//                 {msg.content}
//               </div>
//             ))
//           )}
//         </div>

//         <button
//           onClick={handleSignOut}
//           className="mt-4 bg-red-500 hover:bg-red-600 px-3 py-2 rounded text-sm font-semibold"
//         >
//           Logout
//         </button>
//       </div>

//       {/* Main Content */}
//       <div className="flex-1 flex flex-col items-center overflow-y-auto">
//         <div className="w-[80%] max-w-2xl py-6">
//           {/* Header */}
//           <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight">
//             ReparaturApp,
//           </h1>
//           <br />
//           <h1 className="bg-gradient-to-r from-black via-blue-500 to-violet-800 inline-block text-transparent bg-clip-text font-bold text-5xl leading-tight mb-4">
//             Repair Made Simple
//           </h1>

//           <p className="text-blue-600 leading-tight tracking-tight mb-6 text-lg">
//             Upload a repair manual PDF or ask a general question.
//           </p>

//           {/* Quick Suggestions */}
//           <div className="flex w-full mb-6 gap-3 text-sm text-neutral-800">
//             <div
//               className="group relative grow border border-gray-300 shadow-sm hover:shadow-md hover:bg-neutral-100/30 rounded-xl p-4 transition-all duration-300 cursor-pointer"
//               onClick={(e) => handleSend(e, "How do I replace the filter?")}
//             >
//               How do I replace the filter?
//             </div>
//             <div
//               className="group relative grow border border-gray-300 shadow-sm hover:shadow-md hover:bg-neutral-100/30 rounded-xl p-4 transition-all duration-300 cursor-pointer"
//               onClick={(e) => handleSend(e, "What tools do I need for repair?")}
//             >
//               What tools do I need for repair?
//             </div>
//           </div>

//           {/* Upload Box */}
//           <div className="mb-6">
//             <label className="custum-file-upload">
//               <div className="icon">
//                 <Wrench className="w-12 h-12 text-blue-600" />
//               </div>
//               <div className="text">
//                 <span>{file ? file.name : "Click to upload your PDF"}</span>
//               </div>
//               <input
//                 type="file"
//                 accept="application/pdf"
//                 onChange={handleFileChange}
//               />
//             </label>

//             <div className="mt-3 flex justify-center">
//               <button
//                 onClick={handleUploadPdf}
//                 disabled={uploadStatus === "uploading" || !file}
//                 className={`bg-blue-500 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded ${
//                   uploadStatus === "uploading" || !file
//                     ? "opacity-50 cursor-not-allowed"
//                     : ""
//                 }`}
//               >
//                 {uploadStatus === "uploading" ? "Uploading..." : "Upload"}
//               </button>
//             </div>

//             <div className="mt-2 text-sm text-center">
//               {uploadStatus === "uploaded" && uploadedPdf && (
//                 <span className="text-green-600">
//                   ✅ Uploaded: {uploadedPdf.title}
//                 </span>
//               )}
//               {uploadStatus === "uploading" && (
//                 <span className="text-blue-600">⏳ Uploading...</span>
//               )}
//               {uploadStatus === "error" && (
//                 <span className="text-red-600">❌ Upload failed</span>
//               )}
//               {uploadStatus === "not_uploaded" && file && (
//                 <span className="text-gray-600">⚠️ Not uploaded yet</span>
//               )}
//             </div>
//           </div>

//           {/* Tools Section */}
//           <div className="bg-white p-4 rounded-xl shadow-md mb-6">
//             <h3 className="text-lg font-semibold mb-2">Required Tools & Reusability</h3>
//             {tools.length === 0 ? (
//               <p className="text-gray-500 italic">No tools found.</p>
//             ) : (
//               <div className="space-y-3">
//                 {tools.map((tool) => (
//                   <div key={tool.id} className="border rounded p-3">
//                     <div className="flex justify-between items-start mb-2">
//                       <div>
//                         <p className="font-medium">🛠 {tool.name}</p>
//                         {tool.reusability_score && (
//                           <div className="flex items-center gap-2 mt-1">
//                             <span className="text-sm text-gray-600">Reusability:</span>
//                             <div className="flex">
//                               {[1, 2, 3, 4, 5].map((num) => (
//                                 <span
//                                   key={num}
//                                   className={`text-xs ${
//                                     num <= tool.reusability_score ? "text-green-500" : "text-gray-300"
//                                   }`}
//                                 >
//                                   ★
//                                 </span>
//                               ))}
//                             </div>
//                             <span className="text-xs text-gray-500">({tool.reusability_score}/5)</span>
//                           </div>
//                         )}
//                       </div>
//                       <button
//                         onClick={() => analyzeToolReusability(tool.id)}
//                         className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
//                       >
//                         Analyze
//                       </button>
//                     </div>
//                     {tool.min_price && (
//                       <p className="text-sm text-gray-600">
//                         Price: €{tool.min_price.toFixed(2)}
//                         {tool.max_price && tool.max_price !== tool.min_price && 
//                           ` - €${tool.max_price.toFixed(2)}`
//                         }
//                       </p>
//                     )}
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>

//           {/* Device Management Section */}
//           <div className="bg-white p-4 rounded-xl shadow-md mb-6">
//             <div className="flex justify-between items-center mb-3">
//               <h3 className="text-lg font-semibold">My Devices</h3>
//               <button
//                 onClick={() => setShowDeviceManager(!showDeviceManager)}
//                 className="bg-green-500 hover:bg-green-700 text-white text-sm px-3 py-1 rounded"
//               >
//                 {showDeviceManager ? "Hide" : "Manage"}
//               </button>
//             </div>
            
//             {userDevices.length === 0 ? (
//               <p className="text-gray-500 italic">No devices added yet.</p>
//             ) : (
//               <div className="space-y-2">
//                 {userDevices.map((userDevice) => (
//                   <div 
//                     key={userDevice.id} 
//                     className={`p-3 border rounded cursor-pointer ${
//                       selectedDevice?.id === userDevice.id ? "border-blue-500 bg-blue-50" : "border-gray-300"
//                     }`}
//                     onClick={() => setSelectedDevice(userDevice)}
//                   >
//                     <div className="flex justify-between items-center">
//                       <div>
//                         <p className="font-medium">{userDevice.device?.manufacturer} {userDevice.device?.model}</p>
//                         <p className="text-sm text-gray-600">{userDevice.device?.category}</p>
//                       </div>
//                       <div className="text-right">
//                         <span className={`text-xs px-2 py-1 rounded ${
//                           userDevice.warranty_status === "active" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
//                         }`}>
//                           {userDevice.warranty_status}
//                         </span>
//                         <button
//                           onClick={(e) => {
//                             e.stopPropagation();
//                             checkWarranty(userDevice.id);
//                           }}
//                           className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded"
//                         >
//                           Check Warranty
//                         </button>
//                       </div>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>

//           {/* Repair Analysis Section */}
//           {uploadedPdf && selectedDevice && (
//             <div className="bg-white p-4 rounded-xl shadow-md mb-6">
//               <div className="flex justify-between items-center mb-3">
//                 <h3 className="text-lg font-semibold">Repair Analysis</h3>
//                 <button
//                   onClick={performRepairAnalysis}
//                   className="bg-purple-500 hover:bg-purple-700 text-white text-sm px-3 py-1 rounded"
//                 >
//                   Analyze Repair
//                 </button>
//               </div>
              
//               {showAnalysis && repairAnalysis && (
//                 <div className="space-y-4">
//                   {/* Feasibility */}
//                   {repairAnalysis.feasibility && (
//                     <div className="border-l-4 border-blue-500 pl-4">
//                       <h4 className="font-medium">Repair Feasibility</h4>
//                       <p className={`text-sm ${repairAnalysis.feasibility.is_feasible ? "text-green-600" : "text-red-600"}`}>
//                         {repairAnalysis.feasibility.is_feasible ? "✅ You can perform this repair" : "❌ This repair may be too complex"}
//                       </p>
//                       <p className="text-xs text-gray-600">
//                         Your skill: {repairAnalysis.feasibility.user_skill_score}/5 | Required: {repairAnalysis.feasibility.required_skill_score}/5
//                       </p>
//                       {repairAnalysis.feasibility.warnings.length > 0 && (
//                         <div className="mt-2">
//                           <p className="text-xs font-medium text-orange-600">Warnings:</p>
//                           <ul className="text-xs text-orange-600 list-disc list-inside">
//                             {repairAnalysis.feasibility.warnings.map((warning, idx) => (
//                               <li key={idx}>{warning}</li>
//                             ))}
//                           </ul>
//                         </div>
//                       )}
//                     </div>
//                   )}

//                   {/* Cost & Time */}
//                   {repairAnalysis.costs && repairAnalysis.time && (
//                     <div className="border-l-4 border-green-500 pl-4">
//                       <h4 className="font-medium">Cost & Time Estimate</h4>
//                       <p className="text-sm">
//                         💰 Total Cost: €{repairAnalysis.costs.total_cost.toFixed(2)} 
//                         (Tools: €{repairAnalysis.costs.tools_cost.toFixed(2)}, Parts: €{repairAnalysis.costs.parts_cost.toFixed(2)})
//                       </p>
//                       <p className="text-sm">
//                         ⏱️ Estimated Time: {repairAnalysis.time.total_time_hours.toFixed(1)} hours
//                       </p>
//                     </div>
//                   )}

//                   {/* Comparison */}
//                   {repairAnalysis.comparison && (
//                     <div className="border-l-4 border-yellow-500 pl-4">
//                       <h4 className="font-medium">Self-Repair vs Professional</h4>
//                       <div className="grid grid-cols-2 gap-2 text-sm">
//                         <div>
//                           <p className="font-medium">Self-Repair:</p>
//                           <p>Cost: €{repairAnalysis.comparison.self_repair.cost.toFixed(2)}</p>
//                           <p>Time: {repairAnalysis.comparison.self_repair.time.toFixed(1)}h</p>
//                         </div>
//                         <div>
//                           <p className="font-medium">Professional:</p>
//                           <p>Cost: €{repairAnalysis.comparison.professional_service.cost.toFixed(2)}</p>
//                           <p>Time: {repairAnalysis.comparison.professional_service.time.toFixed(1)}h</p>
//                         </div>
//                       </div>
//                       <p className={`text-sm font-medium mt-2 ${
//                         repairAnalysis.comparison.recommendation === "self_repair" ? "text-green-600" : "text-blue-600"
//                       }`}>
//                         Recommendation: {repairAnalysis.comparison.recommendation === "self_repair" ? "Do it yourself" : "Use professional service"}
//                       </p>
//                     </div>
//                   )}
//                 </div>
//               )}
//             </div>
//           )}

//           {/* User Rating */}
//           <div className="bg-white p-4 rounded-xl shadow-md mb-6">
//             <h3 className="text-lg font-semibold mb-2">Rate Your Expertise</h3>
//             <div className="flex gap-2">
//               {[1, 2, 3, 4, 5].map((num) => (
//                 <button
//                   key={num}
//                   onClick={() => setRating(num)}
//                   className={`px-3 py-1 rounded ${
//                     rating === num ? "bg-blue-600 text-white" : "bg-gray-200"
//                   }`}
//                 >
//                   {num}
//                 </button>
//               ))}
//             </div>
//           </div>

//           {/* Chat Box */}
//           <div className="bg-white p-4 rounded-xl shadow-md max-h-60 overflow-y-auto mb-6">
//             <h3 className="text-lg font-semibold mb-2">Chat</h3>
//             {history.length === 0 ? (
//               <p className="text-gray-500 italic">No messages yet.</p>
//             ) : (
//               <ul className="space-y-2">
//                 {history.map((msg, index) => (
//                   <li
//                     key={index}
//                     className={`p-2 rounded ${
//                       msg.type === "user"
//                         ? "bg-blue-100 text-right"
//                         : "bg-gray-200 text-left"
//                     }`}
//                   >
//                     {msg.content}
//                   </li>
//                 ))}
//               </ul>
//             )}
//           </div>

//           {/* Chat Input */}
//           <form
//             onSubmit={handleSend}
//             className="bg-white h-28 rounded-2xl shadow-md border border-neutral-200 relative"
//           >
//             <div className="flex">
//               <textarea
//                 className="grow m-4 outline-none min-h-16 resize-none"
//                 placeholder="Type your question here ..."
//                 value={question}
//                 onChange={(e) => setQuestion(e.target.value)}
//                 maxLength={4000}
//               />
//             </div>
//             <div className="flex gap-2 items-center absolute right-3 bottom-2">
//               <div className="text-xs text-gray-500">
//                 {question.length}/4000
//               </div>
//               <button
//                 type="submit"
//                 className="bg-neutral-700 rounded-full text-white w-8 h-8 flex items-center justify-center"
//               >
//                 ➤
//               </button>
//             </div>
//           </form>
//         </div>
//       </div>

//       {/* Device Manager Modal */}
//       {showDeviceManager && (
//         <DeviceManager
//           userId={userId}
//           onDeviceAdded={() => {
//             loadUserDevices(userId);
//             setShowDeviceManager(false);
//           }}
//           onClose={() => setShowDeviceManager(false)}
//         />
//       )}
//     </div>
//   );
// }

// export default ReparaturApp;
