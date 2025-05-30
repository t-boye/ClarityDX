// DropdownMenuItem.jsx
import React from "react";

const DropdownMenuItem = ({ children, onClick, className = "" }) => {
  return (
    <div
      onClick={onClick}
      className={`text-sm text-gray-700 hover:bg-gray-200 px-3 py-1 rounded-md cursor-pointer ${className}`}
    >
      {children}
    </div>
  );
};

export default DropdownMenuItem;
