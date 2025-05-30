import React from "react";

const Card = ({ children, className, variant = "default", ...rest }) => {
  let cardClasses = "rounded-lg shadow-md"; // Base classes

  switch (variant) {
    case "elevated":
      cardClasses += " bg-white p-6";
      break;
    case "outlined":
      cardClasses += " border border-gray-200 bg-white p-4";
      break;
    case "flat":
      cardClasses += " bg-gray-50 p-4";
      break;
    default:
      cardClasses += " bg-white p-4";
  }

  return (
    <div className={`${cardClasses} ${className}`} {...rest}>
      {children}
    </div>
  );
};

const CardHeader = ({ children, className }) => {
  return (
    <div className={`p-4 border-b border-gray-100 ${className}`}>
      {children}
    </div>
  );
};

const CardContent = ({ children, className }) => {
  return <div className={`p-4 ${className}`}>{children}</div>;
};

const CardFooter = ({ children, className }) => {
  return (
    <div className={`p-4 border-t border-gray-100 ${className}`}>
      {children}
    </div>
  );
};

// New CardDescription component
const CardDescription = ({ children, className }) => {
  return <p className={`text-sm text-gray-600 ${className}`}>{children}</p>;
};

// New CardTitle component
const CardTitle = ({ children, className }) => {
  return <h3 className={`text-lg font-bold ${className}`}>{children}</h3>;
};

// Export all components including CardTitle
export {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  CardDescription,
  CardTitle,
};
