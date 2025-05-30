// DropdownMenu.jsx
import React from "react";

const DropdownMenu = ({ children, className = "" }) => {
  return <div className={`relative ${className}`}>{children}</div>;
};

export default DropdownMenu;
