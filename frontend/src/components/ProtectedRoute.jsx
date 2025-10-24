import React from 'react';
import { useAuth } from '../hooks/useAuth';

const ProtectedRoute = ({ children }) => {
  const { isLoading: authLoading, isAuthenticated } = useAuth();

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

  // If not authenticated, the useAuth hook will handle redirect
  if (!isAuthenticated()) {
    return null;
  }

  // Render the protected content
  return children;
};

export default ProtectedRoute;