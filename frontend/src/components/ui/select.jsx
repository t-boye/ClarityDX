// /src/components/ui/select.jsx

import React, { useState, useRef, useEffect } from "react";
import { ChevronDownIcon } from "@heroicons/react/20/solid"; // Example icon library

const Select = ({ children, onValueChange }) => {
  const [selectedValue, setSelectedValue] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef(null);

  const handleValueChange = (value) => {
    setSelectedValue(value);
    setIsOpen(false);
    if (onValueChange) {
      onValueChange(value);
    }
  };

  const toggleOpen = () => {
    setIsOpen(!isOpen);
  };

  const handleClickOutside = (event) => {
    if (selectRef.current && !selectRef.current.contains(event.target)) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="relative" ref={selectRef}>
      {React.Children.map(children, (child) => {
        if (child.type === SelectTrigger) {
          return React.cloneElement(child, {
            selectedValue,
            onClick: toggleOpen,
            isOpen,
          });
        }
        if (child.type === SelectContent) {
          return React.cloneElement(child, {
            selectedValue,
            onValueChange: handleValueChange,
            isOpen,
          });
        }
        return child;
      })}
    </div>
  );
};

const SelectTrigger = ({ children, selectedValue, onClick, isOpen }) => {
  return (
    <button
      className={`border rounded p-2 w-full text-left flex items-center justify-between ${
        isOpen ? "border-blue-500 shadow-sm" : ""
      }`}
      onClick={onClick}
    >
      {selectedValue ? (
        <span className="font-semibold">{selectedValue}</span>
      ) : (
        <span className="text-gray-500">{children}</span>
      )}
      <ChevronDownIcon
        className={`w-5 h-5 transition-transform ${
          isOpen ? "transform rotate-180" : ""
        }`}
      />
    </button>
  );
};

const SelectContent = ({ children, selectedValue, onValueChange, isOpen }) => {
  return (
    isOpen && (
      <div className="absolute z-10 mt-1 bg-white border rounded shadow-md w-full">
        {React.Children.map(children, (child) => {
          if (child.type === SelectItem) {
            return React.cloneElement(child, {
              selectedValue,
              onValueChange,
            });
          }
          return child;
        })}
      </div>
    )
  );
};

const SelectItem = ({ children, value, selectedValue, onValueChange }) => {
  const isSelected = value === selectedValue;
  return (
    <button
      className={`block w-full text-left p-2 hover:bg-gray-100 ${
        isSelected ? "bg-blue-100" : ""
      }`}
      onClick={() => onValueChange(value)}
    >
      {children}
    </button>
  );
};

const SelectValue = ({ placeholder }) => {
  return <span className="text-gray-500">{placeholder}</span>;
};

export { SelectTrigger, SelectContent, SelectItem, SelectValue };

export default Select;
