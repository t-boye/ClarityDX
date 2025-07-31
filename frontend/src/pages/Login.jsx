import React, { useState } from "react";
import { auth } from "../firebase";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
} from "firebase/auth";
import { useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FiEye, FiEyeOff, FiArrowRight, FiArrowLeft } from "react-icons/fi";

const IMAGE_URL =
  "https://i.postimg.cc/kG0thqBg/Google-Made-An-AI-Doctor-That-Can-Help-Diagnose-Patients-BGR.jpg";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState("");
  const [isHovered, setIsHovered] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate(from, { replace: true });
    } catch (error) {
      setError("Invalid email or password. Please check your credentials.");
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      await createUserWithEmailAndPassword(auth, email, password);
      setIsRegistering(false);
      setSuccess("Registration successful! Please log in.");
    } catch (error) {
      let errorMessage = "Registration failed. Please try again.";
      if (error.code === "auth/email-already-in-use") {
        errorMessage =
          "Email already in use. Please use a different email or log in.";
      } else if (error.code === "auth/invalid-email") {
        errorMessage = "Invalid email format.";
      } else if (error.code === "auth/weak-password") {
        errorMessage = "Password should be at least 6 characters.";
      }
      setError(errorMessage);
    }
  };

  // Animation variants for desktop only
  const containerVariants = {
    login: {
      x: 0,
      transition: { type: "spring", stiffness: 100, damping: 15 },
    },
    register: {
      x: "100%",
      transition: { type: "spring", stiffness: 100, damping: 15 },
    },
  };

  const formVariants = {
    login: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.3 },
    },
    register: {
      opacity: 1,
      x: "-100%",
      transition: { duration: 0.3 },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center p-4 md:p-8 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute top-0 left-0 w-32 h-32 bg-blue-200 rounded-full filter blur-3xl opacity-30"></div>
      <div className="absolute bottom-0 right-0 w-64 h-64 bg-teal-200 rounded-full filter blur-3xl opacity-30"></div>

      {/* Main container - different behavior on mobile vs desktop */}
      <div className="relative z-10 w-full max-w-4xl flex flex-col md:flex-row bg-white bg-opacity-95 border border-blue-100 rounded-2xl shadow-2xl backdrop-blur-lg overflow-hidden transition-all duration-300">
        {/* Image container - hidden on mobile, animated on desktop */}
        <AnimatePresence>
          {!isRegistering && ( // Only show image on login view for mobile
            <motion.div
              className={`hidden md:flex items-center justify-center w-full md:w-1/2 p-4 lg:p-8 bg-gradient-to-br from-blue-50 to-teal-50`}
              variants={containerVariants}
              animate={isRegistering ? "register" : "login"}
              initial={false}
            >
              <div className="relative w-full h-full min-h-[300px] overflow-hidden rounded-xl">
                <img
                  src={IMAGE_URL}
                  alt="Visual"
                  className="w-full h-full object-cover rounded-xl shadow-lg"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
                <div className="absolute bottom-4 left-4 right-4 text-white">
                  <motion.h3
                    className="text-xl lg:text-2xl font-bold mb-1 lg:mb-2"
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    {isRegistering ? "Join Our Community" : "Welcome Back"}
                  </motion.h3>
                  <motion.p
                    className="text-xs lg:text-sm opacity-90"
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    {isRegistering
                      ? "Start your journey to better health today"
                      : "Your health data, all in one place"}
                  </motion.p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Form container - static on mobile, animated on desktop */}
        <motion.div
          className="flex-1 flex flex-col items-center justify-center py-8 md:py-10 px-4 sm:px-6 md:px-8 lg:px-10 min-h-[500px] md:min-h-[600px]"
          variants={{}}
          animate={{}}
        >
          {/* Mobile-only header for register view */}
          {isRegistering && (
            <div className="md:hidden w-full text-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">
                Create Account
              </h2>
              <p className="text-gray-600 text-sm">
                Join our health community today
              </p>
            </div>
          )}

          {/* Logo */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="mb-4 md:mb-6"
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
          >
            <div className="w-16 h-16 md:w-20 md:h-20 lg:w-24 lg:h-24 rounded-full bg-white shadow-lg flex items-center justify-center relative overflow-hidden">
              <motion.img
                src="/T-logo-removed.png"
                alt="App Logo"
                className="w-10 h-10 md:w-12 md:h-12 lg:w-16 lg:h-16 z-10"
                animate={{
                  rotate: isHovered ? [0, 15, -15, 0] : 0,
                  scale: isHovered ? 1.1 : 1,
                }}
                transition={{
                  duration: 0.6,
                  type: "spring",
                }}
              />
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-blue-600 to-teal-600"
                initial={{ opacity: 0 }}
                animate={{ opacity: isHovered ? 0.2 : 0 }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </motion.div>

          {/* Title - hidden on mobile when registering */}
          {!isRegistering && (
            <motion.h2 className="text-2xl md:text-3xl font-bold text-gray-800 mb-1 md:mb-2 text-center">
              Welcome Back
            </motion.h2>
          )}

          {/* Subtitle - hidden on mobile when registering */}
          {!isRegistering && (
            <motion.p className="text-gray-600 mb-4 md:mb-6 text-center max-w-xs text-sm md:text-base">
              Sign in to access your dashboard
            </motion.p>
          )}

          {/* Messages */}
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="w-full p-2 md:p-3 mb-3 md:mb-4 bg-green-50 text-green-700 rounded-lg text-xs md:text-sm flex items-center"
            >
              <svg
                className="w-4 h-4 md:w-5 md:h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
              {success}
            </motion.div>
          )}

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="w-full p-2 md:p-3 mb-3 md:mb-4 bg-red-50 text-red-600 rounded-lg text-xs md:text-sm flex items-center"
            >
              <svg
                className="w-4 h-4 md:w-5 md:h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
              {error}
            </motion.div>
          )}

          {/* Form */}
          <form
            onSubmit={isRegistering ? handleRegister : handleEmailLogin}
            className="w-full max-w-xs sm:max-w-sm"
          >
            <div className="mb-3 md:mb-4">
              <label
                htmlFor="email"
                className="block text-gray-700 text-xs md:text-sm font-medium mb-1"
              >
                Email
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full p-2 md:p-3 text-xs md:text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-200 focus:border-blue-500 placeholder:text-gray-400 transition pl-8 md:pl-10"
                />
                <div className="absolute inset-y-0 left-0 pl-2 md:pl-3 flex items-center pointer-events-none text-gray-400">
                  <svg
                    className="w-4 h-4 md:w-5 md:h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    ></path>
                  </svg>
                </div>
              </div>
            </div>

            <div className="mb-4 md:mb-6 relative">
              <label
                htmlFor="password"
                className="block text-gray-700 text-xs md:text-sm font-medium mb-1"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full p-2 md:p-3 text-xs md:text-sm border border-gray-300 rounded-xl focus:ring-4 focus:ring-blue-200 focus:border-blue-500 placeholder:text-gray-400 transition pl-8 md:pl-10 pr-8 md:pr-10"
                />
                <div className="absolute inset-y-0 left-0 pl-2 md:pl-3 flex items-center pointer-events-none text-gray-400">
                  <svg
                    className="w-4 h-4 md:w-5 md:h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    ></path>
                  </svg>
                </div>
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-2 md:pr-3 flex items-center text-gray-500 hover:text-gray-700"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  tabIndex={0}
                >
                  {showPassword ? <FiEyeOff size={16} /> : <FiEye size={16} />}
                </button>
              </div>
              {isRegistering && (
                <p className="text-xs text-gray-500 mt-1">
                  Password must be at least 6 characters
                </p>
              )}
            </div>

            <motion.button
              type="submit"
              whileHover={{
                scale: ["md", "lg"].includes(window.innerWidth > 768)
                  ? 1.02
                  : 1,
              }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-500 hover:to-teal-500 text-white p-2 md:p-3 text-sm md:text-base rounded-xl font-semibold shadow-lg transition duration-200 flex items-center justify-center"
            >
              {isRegistering ? "Sign Up" : "Login"}
              <span className="ml-1 md:ml-2">
                {isRegistering ? (
                  <FiArrowRight size={16} />
                ) : (
                  <FiArrowRight size={16} />
                )}
              </span>
            </motion.button>
          </form>

          {/* Toggle link */}
          <div className="mt-4 md:mt-6 text-center text-xs md:text-sm text-gray-600 flex items-center justify-center">
            {isRegistering
              ? "Already have an account?"
              : "Don't have an account?"}
            <button
              onClick={() => {
                setIsRegistering(!isRegistering);
                setError("");
                setSuccess("");
              }}
              className="ml-1 text-blue-600 font-medium hover:underline flex items-center"
            >
              {isRegistering ? "Login here" : "Sign up now"}
              <span className="ml-1">
                {isRegistering ? (
                  <FiArrowLeft size={14} />
                ) : (
                  <FiArrowRight size={14} />
                )}
              </span>
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
