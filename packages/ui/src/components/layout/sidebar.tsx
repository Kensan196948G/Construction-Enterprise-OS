import * as React from "react"
import { cn } from "../../lib/utils"

interface SidebarProps extends React.HTMLAttributes<HTMLElement> {
  header?: React.ReactNode
  footer?: React.ReactNode
  children?: React.ReactNode
}

export function Sidebar({
  header,
  footer,
  children,
  className,
  ...props
}: SidebarProps) {
  return (
    <nav className={cn("flex flex-col h-full", className)} {...props}>
      {header && (
        <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6 shrink-0">
          {header}
        </div>
      )}
      <div className="flex-1 overflow-y-auto px-3 py-4">{children}</div>
      {footer && (
        <div className="border-t border-gray-200 p-4 shrink-0">{footer}</div>
      )}
    </nav>
  )
}

interface SidebarNavProps extends React.HTMLAttributes<HTMLUListElement> {
  children: React.ReactNode
}

export function SidebarNav({ children, className, ...props }: SidebarNavProps) {
  return (
    <ul className={cn("space-y-1", className)} {...props}>
      {children}
    </ul>
  )
}

interface SidebarNavItemProps
  extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  icon?: React.ReactNode
  active?: boolean
  badge?: React.ReactNode
}

export const SidebarNavItem = React.forwardRef<
  HTMLAnchorElement,
  SidebarNavItemProps
>(({ icon, active, badge, children, className, ...props }, ref) => {
  return (
    <li>
      <a
        ref={ref}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors cursor-pointer",
          active
            ? "bg-primary-50 text-primary-700"
            : "text-gray-700 hover:bg-gray-100",
          className
        )}
        {...props}
      >
        {icon && <span className="h-5 w-5 flex-shrink-0">{icon}</span>}
        <span className="flex-1 truncate">{children}</span>
        {badge}
      </a>
    </li>
  )
})
SidebarNavItem.displayName = "SidebarNavItem"
