import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import robotImg from "../assets/reparatur-plattform.svg";

function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [skillLevel, setSkillLevel] = useState(1);
  const [physicalStrength, setPhysicalStrength] = useState(3);
  const [availableSpace, setAvailableSpace] = useState(3);
  const [experienceLevel, setExperienceLevel] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/users/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          username, 
          password, 
          skill_level: skillLevel,
          physical_strength: physicalStrength,
          available_space: availableSpace,
          experience_level: experienceLevel
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to create user");
      }

      alert("Signup successful! You can now login.");
      navigate("/"); // redirect to login
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-400 h-screen w-screen flex items-center justify-center px-4">
      <div className="flex rounded-lg shadow-lg w-full sm:w-3/4 lg:w-1/2 bg-white">
        {/* Left column - form */}
        <div className="flex flex-col w-full md:w-1/2 p-6">
          <div className="flex flex-col flex-1 justify-center">
            <h1 className="text-3xl text-center font-thin mb-6">
              Create Account
            </h1>

            {error && (
              <p className="text-red-600 text-center text-sm mb-3">{error}</p>
            )}

            <form
              onSubmit={handleSignup}
              className="form-horizontal w-3/4 mx-auto"
            >
              {/* Username */}
              <div className="flex flex-col mt-4">
                <input
                  id="username"
                  type="text"
                  className="flex-grow h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  name="username"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              {/* Password */}
              <div className="flex flex-col mt-4">
                <input
                  id="password"
                  type="password"
                  className="flex-grow h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  name="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              {/* Confirm Password */}
              <div className="flex flex-col mt-4">
                <input
                  id="confirmPassword"
                  type="password"
                  className="flex-grow h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  name="confirmPassword"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>

              {/* Profile Section */}
              <div className="mt-6 border-t pt-4">
                <h3 className="text-lg font-medium mb-4 text-center">Your Skills & Preferences</h3>
                
                {/* Skill Level */}
                <div className="flex flex-col mt-3">
                  <label className="text-sm font-medium text-gray-700 mb-1">Overall Skill Level</label>
                  <select
                    value={skillLevel}
                    onChange={(e) => setSkillLevel(parseInt(e.target.value))}
                    className="h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  >
                    <option value={1}>1 - Beginner</option>
                    <option value={2}>2 - Novice</option>
                    <option value={3}>3 - Intermediate</option>
                    <option value={4}>4 - Advanced</option>
                    <option value={5}>5 - Expert</option>
                  </select>
                </div>

                {/* Physical Strength */}
                <div className="flex flex-col mt-3">
                  <label className="text-sm font-medium text-gray-700 mb-1">Physical Strength</label>
                  <select
                    value={physicalStrength}
                    onChange={(e) => setPhysicalStrength(parseInt(e.target.value))}
                    className="h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  >
                    <option value={1}>1 - Limited</option>
                    <option value={2}>2 - Light work</option>
                    <option value={3}>3 - Moderate</option>
                    <option value={4}>4 - Strong</option>
                    <option value={5}>5 - Very strong</option>
                  </select>
                </div>

                {/* Available Space */}
                <div className="flex flex-col mt-3">
                  <label className="text-sm font-medium text-gray-700 mb-1">Available Workspace</label>
                  <select
                    value={availableSpace}
                    onChange={(e) => setAvailableSpace(parseInt(e.target.value))}
                    className="h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  >
                    <option value={1}>1 - Very limited</option>
                    <option value={2}>2 - Small space</option>
                    <option value={3}>3 - Moderate</option>
                    <option value={4}>4 - Large space</option>
                    <option value={5}>5 - Workshop/Garage</option>
                  </select>
                </div>

                {/* Experience Level */}
                <div className="flex flex-col mt-3">
                  <label className="text-sm font-medium text-gray-700 mb-1">Repair Experience</label>
                  <select
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(parseInt(e.target.value))}
                    className="h-10 px-3 border rounded border-gray-400 focus:outline-none focus:border-gray-500"
                  >
                    <option value={1}>1 - No experience</option>
                    <option value={2}>2 - Few repairs</option>
                    <option value={3}>3 - Some experience</option>
                    <option value={4}>4 - Experienced</option>
                    <option value={5}>5 - Very experienced</option>
                  </select>
                </div>
              </div>

              {/* Button */}
              <div className="flex flex-col mt-8">
                <button
                  type="submit"
                  disabled={loading}
                  className={`bg-blue-500 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded ${
                    loading ? "opacity-50 cursor-not-allowed" : ""
                  }`}
                >
                  {loading ? "Signing up..." : "Sign Up"}
                </button>
              </div>
            </form>

            {/* Links */}
            <div className="text-center mt-4">
              <Link
                to="/"
                className="no-underline hover:underline text-blue-500 text-xs"
              >
                Already have an account? Login
              </Link>
            </div>
          </div>
        </div>

        {/* Right column - robot image */}
        <div className="hidden md:flex md:w-1/2 items-center justify-center bg-gray-100 rounded-r-lg">
          <img
            src={robotImg}
            alt="Repair Bot"
            className="max-h-full max-w-full object-contain p-6"
          />
        </div>
      </div>
    </div>
  );
}

export default Signup;
