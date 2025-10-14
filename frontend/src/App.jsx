import { BrowserRouter, Routes, Route } from "react-router-dom";
 import Login from "./pages/login.jsx";
 import Signup from "./pages/signup.jsx";
 import Chatbot from "./pages/chatbot.jsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/chat" element={<Chatbot />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
