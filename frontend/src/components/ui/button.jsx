import React from "react";

const Button = ({
  children,
  onClick,
  className,
  type = "button",
  variant = "primary",
  size = "medium",
  disabled = false,
  ...rest
}) => {
  let buttonClasses =
    "rounded-lg transition focus:outline-none focus:ring-2 focus:ring-offset-2"; // Base classes

  // Size variations
  switch (size) {
    case "small":
      buttonClasses += " px-3 py-1 text-sm";
      break;
    case "large":
      buttonClasses += " px-6 py-3 text-lg";
      break;
    default:
      buttonClasses += " px-4 py-2"; // Medium size
  }

  // Variant variations
  switch (variant) {
    case "secondary":
      buttonClasses +=
        " bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500";
      break;
    case "outlined":
      buttonClasses +=
        " border border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500";
      break;
    case "text":
      buttonClasses += " text-blue-600 hover:bg-blue-50 focus:ring-blue-500";
      break;
    case "danger":
      buttonClasses +=
        " bg-red-600 text-white hover:bg-red-700 focus:ring-red-500";
      break;
    case "success":
      buttonClasses +=
        " bg-green-600 text-white hover:bg-green-700 focus:ring-green-500";
      break;
    default:
      buttonClasses +=
        " bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500"; // Primary
  }

  // Disabled state
  if (disabled) {
    buttonClasses += " opacity-50 cursor-not-allowed";
  }

  return (
    <button
      type={type}
      onClick={onClick}
      className={`${buttonClasses} ${className}`}
      disabled={disabled}
      {...rest}
    >
      {children}
    </button>
  );
};

export { Button };
