import * as React from "react";
import * as RadixDialog from "@radix-ui/react-dialog"; // Changed import
import { cn } from "@/lib/utils";
import * as DialogPrimitive from "@radix-ui/react-dialog";

export function Dialog({ children, className, open, onOpenChange, ...props }) {
  return (
    <RadixDialog.Root open={open} onOpenChange={onOpenChange} {...props}>
      <div
        className={cn(
          "fixed inset-0 flex items-center justify-center",
          className
        )}
      >
        {children}
      </div>
    </RadixDialog.Root>
  );
}

export function DialogTrigger({ children, ...props }) {
  return <RadixDialog.Trigger {...props}>{children}</RadixDialog.Trigger>;
}

export function DialogContent({ children, className, ...props }) {
  return (
    <RadixDialog.Content
      className={cn("bg-white p-6 rounded-lg shadow-lg", className)}
      {...props}
    >
      {children}
    </RadixDialog.Content>
  );
}

export function DialogHeader({ children }) {
  return <div className="mb-4">{children}</div>;
}

export function DialogTitle({ children }) {
  return <h2 className="text-lg font-bold">{children}</h2>;
}

export function DialogDescription({ children, className, ...props }) {
  return (
    <DialogPrimitive.Description
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    >
      {children}
    </DialogPrimitive.Description>
  );
}

export function DialogFooter({ children, className, ...props }) {
  return (
    <div
      className={cn(
        "flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
