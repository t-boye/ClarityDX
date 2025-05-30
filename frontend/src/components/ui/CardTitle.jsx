// CardTitle.jsx
import React from "react";

const CardTitle = ({ children, className = "" }) => {
  return <h2 className={`text-xl font-semibold ${className}`}>{children}</h2>;
};

export default CardTitle;
