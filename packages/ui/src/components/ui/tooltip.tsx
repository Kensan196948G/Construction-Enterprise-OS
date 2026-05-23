import * as React from "react"
import { cn } from "../../lib/utils"

interface TooltipContextValue {
  open: boolean
  setOpen: (open: boolean) => void
}

const TooltipContext = React.createContext<TooltipContextValue>({
  open: false,
  setOpen: () => {},
})

function TooltipProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}

function Tooltip({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false)
  return (
    <TooltipContext.Provider value={{ open, setOpen }}>
      <div
        className="relative inline-block"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
      >
        {children}
      </div>
    </TooltipContext.Provider>
  )
}

function TooltipTrigger({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("cursor-pointer", className)} {...props}>
      {children}
    </div>
  )
}

const TooltipContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => {
  const { open } = React.useContext(TooltipContext)
  if (!open) return null

  return (
    <div
      ref={ref}
      className={cn(
        "absolute bottom-full left-1/2 z-50 -translate-x-1/2 mb-2 rounded-md bg-gray-900 px-3 py-1.5 text-xs text-white shadow-md",
        className
      )}
      {...props}
    />
  )
})
TooltipContent.displayName = "TooltipContent"

export { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent }
