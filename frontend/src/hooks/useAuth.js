import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const useAuth = () => {
  const [userId, setUserId] = useState(null);
  const [rating, setRating] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = () => {
      try {
        const storedUser = localStorage.getItem("user");
        
        if (!storedUser) {
          setIsLoading(false);
          // Don't navigate immediately on page load - let the component decide
          return;
        }

        const parsed = JSON.parse(storedUser);
        
        // Validate user data structure
        if (!parsed.id) {
          console.warn("Invalid user data in localStorage");
          localStorage.removeItem("user");
          setIsLoading(false);
          return;
        }

        setUser(parsed);
        setUserId(parsed.id);
        
        // Initialize rating from user's skill level (default to 3 if not available)
        const userSkillLevel = parsed.skill_level || 3;
        setRating(userSkillLevel);
        
        setIsLoading(false);
      } catch (error) {
        console.error("Error parsing stored user data:", error);
        localStorage.removeItem("user");
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Separate effect for navigation to avoid infinite redirects
  useEffect(() => {
    if (!isLoading && !userId && window.location.pathname !== "/" && window.location.pathname !== "/signup") {
      navigate("/");
    }
  }, [userId, isLoading, navigate]);

  const handleSignOut = () => {
    // Clear all localStorage data
    localStorage.removeItem('user');
    localStorage.removeItem('uploadedPdf');
    localStorage.removeItem('currentConversation');
    localStorage.removeItem('chatHistory');
    
    // Reset state
    setUserId(null);
    setUser(null);
    setRating(1);
    
    // Navigate to login
    navigate("/");
  };

  const isAuthenticated = () => {
    return !isLoading && userId !== null;
  };

  return {
    userId,
    rating,
    user,
    isLoading,
    isAuthenticated,
    handleSignOut
  };
};