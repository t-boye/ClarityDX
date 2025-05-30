// Badge.jsx
import React from "react";

const Badge = ({ children, className = "" }) => {
  return (
    <span
      className={`bg-green-500 text-white rounded-full px-3 py-1 text-xs ${className}`}
    >
      {children}
    </span>
  );
};

export default Badge;
