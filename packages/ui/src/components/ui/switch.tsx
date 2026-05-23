import * as React from "react"
import { cn } from "../../lib/utils"

const Switch = React.forwardRef<
  HTMLInputElement,
  Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> & {
    label?: string
  }
>(({ className, label, id, ...props }, ref) => {
  const switchId = id || React.useId()

  return (
    <div className="flex items-center gap-2">
      <label
        htmlFor={switchId}
        className="relative inline-flex cursor-pointer items-center"
      >
        <input
          ref={ref}
          type="checkbox"
          id={switchId}
          className="peer sr-only"
          {...props}
        />
        <div
          className={cn(
            "h-5 w-9 rounded-full bg-gray-300 peer-checked:bg-primary-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary-500/20 transition-colors",
            "after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:h-4 after:w-4 after:rounded-full after:bg-white after:shadow-sm after:transition-transform peer-checked:after:translate-x-[18px]",
            className
          )}
        />
      </label>
      {label && (
        <span className="text-sm font-medium text-gray-700 select-none">
          {label}
        </span>
      )}
    </div>
  )
})
Switch.displayName = "Switch"

export { Switch }
