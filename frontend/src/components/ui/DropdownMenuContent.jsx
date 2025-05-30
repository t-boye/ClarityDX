// DropdownMenuContent.jsx
import React from "react";

const DropdownMenuContent = ({ children, className = "" }) => {
  return (
    <div className={`absolute bg-white shadow-lg rounded-md p-2 ${className}`}>
      {children}
    </div>
  );
};

export default DropdownMenuContent;
