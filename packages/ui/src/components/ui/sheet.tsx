import * as React from "react"
import { cn } from "../../lib/utils"
import { X } from "lucide-react"

interface SheetProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  side?: "left" | "right"
  children: React.ReactNode
}

function Sheet({ open, onOpenChange, side = "left", children }: SheetProps) {
  if (!open) return null

  return (
    <>
      <div
        className="fixed inset-0 z-50 bg-black/50"
        onClick={() => onOpenChange?.(false)}
      />
      <div
        className={`fixed inset-y-0 z-50 w-full max-w-sm bg-white shadow-xl ${
          side === "left" ? "left-0" : "right-0"
        }`}
      >
        {children}
      </div>
    </>
  )
}

const SheetContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("flex flex-col h-full", className)} {...props}>
    {children}
  </div>
))
SheetContent.displayName = "SheetContent"

const SheetHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex items-center justify-between border-b border-gray-200 px-6 py-4",
      className
    )}
    {...props}
  />
)

const SheetTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h2
    ref={ref}
    className={cn("text-lg font-bold text-gray-900", className)}
    {...props}
  />
))
SheetTitle.displayName = "SheetTitle"

interface SheetCloseProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  onClose?: () => void
}

const SheetClose = React.forwardRef<HTMLButtonElement, SheetCloseProps>(
  ({ className, onClose, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "rounded-sm opacity-70 hover:opacity-100 transition-opacity",
        className
      )}
      onClick={onClose}
      {...props}
    >
      <X className="h-5 w-5" />
      <span className="sr-only">Close</span>
    </button>
  )
)
SheetClose.displayName = "SheetClose"

export { Sheet, SheetContent, SheetHeader, SheetTitle, SheetClose }
