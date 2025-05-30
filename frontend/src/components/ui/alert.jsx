import React from "react";

// Alert component
export const Alert = ({ variant = "info", children }) => {
  const alertStyles = {
    info: "bg-blue-100 text-blue-700 border border-blue-300",
    success: "bg-green-100 text-green-700 border border-green-300",
    warning: "bg-yellow-100 text-yellow-700 border border-yellow-300",
    error: "bg-red-100 text-red-700 border border-red-300",
  };

  return (
    <div
      className={`p-4 rounded-md ${alertStyles[variant]} flex items-center`}
      role="alert"
    >
      {children}
    </div>
  );
};

// AlertTitle component
export const AlertTitle = ({ children }) => {
  return <strong className="font-bold">{children}</strong>;
};

// AlertDescription component
export const AlertDescription = ({ children }) => {
  return <span className="block">{children}</span>;
};
