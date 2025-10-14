import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const useAuth = () => {
  const [userId, setUserId] = useState(null);
  const [rating, setRating] = useState(1);
  const navigate = useNavigate();

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
    } catch {
      navigate("/");
    }
  }, [navigate]);

  const handleSignOut = () => {
    // Clear all localStorage data
    localStorage.removeItem('user');
    localStorage.removeItem('uploadedPdf');
    
    // Navigate to login
    navigate("/");
  };

  return {
    userId,
    rating,
    handleSignOut
  };
};