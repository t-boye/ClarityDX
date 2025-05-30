// Avatar.jsx
import React from "react";

const Avatar = ({ src, alt, className = "" }) => {
  return (
    <div className={`w-12 h-12 rounded-full overflow-hidden ${className}`}>
      <img src={src} alt={alt} className="w-full h-full object-cover" />
    </div>
  );
};

export default Avatar;
