import * as React from "react"
import { cn } from "../../lib/utils"

interface AppShellProps extends React.HTMLAttributes<HTMLDivElement> {
  sidebar: React.ReactNode
  header: React.ReactNode
  children: React.ReactNode
  sidebarWidth?: string
}

export function AppShell({
  sidebar,
  header,
  children,
  sidebarWidth = "w-64",
  className,
  ...props
}: AppShellProps) {
  return (
    <div
      className={cn("flex h-screen overflow-hidden bg-gray-50", className)}
      {...props}
    >
      <aside
        className={cn(
          "hidden lg:flex flex-col border-r border-gray-200 bg-white shrink-0",
          sidebarWidth
        )}
      >
        {sidebar}
      </aside>
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center gap-4 border-b border-gray-200 bg-white px-6 shrink-0">
          {header}
        </header>
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}

interface MobileAppShellProps extends React.HTMLAttributes<HTMLDivElement> {
  sidebar: React.ReactNode
  header: React.ReactNode
  children: React.ReactNode
  sidebarOpen: boolean
  onSidebarClose: () => void
}

export function MobileAppShell({
  sidebar,
  header,
  children,
  sidebarOpen,
  onSidebarClose,
  className,
  ...props
}: MobileAppShellProps) {
  return (
    <div
      className={cn("flex h-screen overflow-hidden bg-gray-50", className)}
      {...props}
    >
      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onSidebarClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col transition-transform duration-200 lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {sidebar}
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center gap-4 border-b border-gray-200 bg-white px-4 lg:px-6 shrink-0">
          {header}
        </header>
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}
