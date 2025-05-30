import React from "react";
import { cn } from "@/lib/utils"; // Only if you're using a `cn` utility to combine classNames

const CardContent = React.forwardRef(
  ({ className, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("p-4 pt-0", className)} {...props}>
        {children}
      </div>
    );
  }
);

CardContent.displayName = "CardContent";

export default CardContent;
