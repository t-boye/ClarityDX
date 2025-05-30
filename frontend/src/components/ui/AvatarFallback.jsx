// AvatarFallback.jsx
import React from "react";

const AvatarFallback = ({ children, className = "" }) => {
  return (
    <div
      className={`w-12 h-12 rounded-full bg-gray-300 text-center flex items-center justify-center text-white ${className}`}
    >
      {children}
    </div>
  );
};

export default AvatarFallback;
