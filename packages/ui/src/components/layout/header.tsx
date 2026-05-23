import * as React from "react"
import { cn } from "../../lib/utils"
import { Menu } from "lucide-react"

interface HeaderProps extends React.HTMLAttributes<HTMLElement> {
  branding?: React.ReactNode
  actions?: React.ReactNode
  onMenuClick?: () => void
  showMenuButton?: boolean
}

export function Header({
  branding,
  actions,
  onMenuClick,
  showMenuButton = false,
  className,
  ...props
}: HeaderProps) {
  return (
    <header
      className={cn(
        "flex h-full w-full items-center gap-4",
        className
      )}
      {...props}
    >
      {showMenuButton && (
        <button
          className="lg:hidden text-gray-500 hover:text-gray-700"
          onClick={onMenuClick}
          aria-label="メニューを開く"
        >
          <Menu className="h-6 w-6" />
        </button>
      )}

      {branding && (
        <div className="flex items-center gap-2 flex-shrink-0">
          {branding}
        </div>
      )}

      <div className="flex-1" />

      {actions && (
        <div className="flex items-center gap-2">{actions}</div>
      )}
    </header>
  )
}
