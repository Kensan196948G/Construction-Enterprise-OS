import * as React from "react"
import { cn } from "../../lib/utils"
import { Check } from "lucide-react"

const Checkbox = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement> & { label?: string }
>(({ className, label, id, ...props }, ref) => {
  const checkboxId = id || React.useId()

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex items-center">
        <input
          ref={ref}
          type="checkbox"
          id={checkboxId}
          className={cn(
            "peer h-4 w-4 appearance-none rounded border border-concrete-300 bg-white checked:bg-primary-600 checked:border-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500/20 cursor-pointer transition-colors",
            className
          )}
          {...props}
        />
        <Check className="pointer-events-none absolute left-0 top-0 h-4 w-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
      </div>
      {label && (
        <label
          htmlFor={checkboxId}
          className="text-sm font-medium text-gray-700 cursor-pointer select-none"
        >
          {label}
        </label>
      )}
    </div>
  )
})
Checkbox.displayName = "Checkbox"

export { Checkbox }
