import * as React from "react"
import { cn } from "../../lib/utils"

interface DropdownMenuContextValue {
  open: boolean
  setOpen: (open: boolean) => void
}

const DropdownMenuContext = React.createContext<DropdownMenuContextValue>({
  open: false,
  setOpen: () => {},
})

function DropdownMenu({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false)
  const ref = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside)
      return () => document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [open])

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div ref={ref} className="relative inline-block">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  )
}

function DropdownMenuTrigger({
  children,
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const { open, setOpen } = React.useContext(DropdownMenuContext)

  return (
    <button
      type="button"
      className={cn("focus:outline-none", className)}
      onClick={() => setOpen(!open)}
      {...props}
    >
      {children}
    </button>
  )
}

const DropdownMenuContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { align?: "start" | "end" }
>(({ className, align = "start", ...props }, ref) => {
  const { open } = React.useContext(DropdownMenuContext)
  if (!open) return null

  return (
    <div
      ref={ref}
      className={cn(
        "absolute top-full z-50 mt-1 min-w-[12rem] rounded-lg border border-gray-200 bg-white p-1 shadow-lg animate-in fade-in-0 zoom-in-95",
        align === "end" ? "right-0" : "left-0",
        className
      )}
      {...props}
    />
  )
})
DropdownMenuContent.displayName = "DropdownMenuContent"

const DropdownMenuItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { inset?: boolean }
>(({ className, inset, ...props }, ref) => {
  const { setOpen } = React.useContext(DropdownMenuContext)

  return (
    <div
      ref={ref}
      role="menuitem"
      className={cn(
        "relative flex cursor-pointer select-none items-center rounded-md px-3 py-2 text-sm text-gray-700 outline-none hover:bg-gray-100 hover:text-gray-900 transition-colors",
        inset && "pl-8",
        className
      )}
      onClick={() => setOpen(false)}
      {...props}
    />
  )
})
DropdownMenuItem.displayName = "DropdownMenuItem"

const DropdownMenuSeparator = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("my-1 h-px bg-gray-200", className)}
    {...props}
  />
))
DropdownMenuSeparator.displayName = "DropdownMenuSeparator"

const DropdownMenuLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("px-3 py-2 text-xs font-semibold text-gray-500", className)}
    {...props}
  />
))
DropdownMenuLabel.displayName = "DropdownMenuLabel"

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
}
