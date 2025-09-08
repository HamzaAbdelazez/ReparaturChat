import React, {useState} from "react";
import {Link, useNavigate} from "react-router-dom";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const response = await fetch("http://localhost:8000/users/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({username, password}),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Login failed");
            }

            const user = await response.json();
            localStorage.setItem("user", JSON.stringify(user));
            navigate("/chat");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <form
                onSubmit={handleLogin}
                className="bg-white p-8 rounded-lg shadow-lg w-80 space-y-4"
            >
                <h2 className="text-3xl font-bold text-center text-blue-600">Login</h2>

                {error && (
                    <p className="text-red-600 text-center text-sm font-medium">{error}</p>
                )}

                <input
                    type="text"
                    placeholder="Username"
                    className="w-full border p-2 rounded"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />

                <input
                    type="password"
                    placeholder="Password"
                    className="w-full border p-2 rounded"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <button
                    type="submit"
                    disabled={loading}
                    className={`w-full bg-blue-600 text-white px-6 py-4 rounded hover:bg-blue-700 ${
                        loading ? "opacity-70 cursor-not-allowed" : ""
                    }`}
                >
                    {loading ? "Logging in..." : "Login"}
                </button>

                <p className="text-sm text-center">
                    Don't have an account?{" "}
                    <Link to="/signup" className="text-blue-600 hover:underline">
                        Sign up
                    </Link>
                </p>
            </form>
        </div>
    );
}

export default Login;
