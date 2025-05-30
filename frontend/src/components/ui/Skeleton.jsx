// Skeleton.jsx
import React from "react";

const Skeleton = ({ className = "" }) => {
  return <div className={`bg-gray-200 animate-pulse ${className}`}></div>;
};

export default Skeleton;
