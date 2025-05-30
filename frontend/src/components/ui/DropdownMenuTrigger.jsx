// DropdownMenuTrigger.jsx
import React from "react";

const DropdownMenuTrigger = ({ children, onClick, className = "" }) => {
  return (
    <button
      onClick={onClick}
      className={`bg-gray-100 text-black px-4 py-2 rounded-md ${className}`}
    >
      {children}
    </button>
  );
};

export default DropdownMenuTrigger;
