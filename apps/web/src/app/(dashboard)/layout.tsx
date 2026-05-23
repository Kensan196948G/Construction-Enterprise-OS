'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  ClipboardList,
  FileText,
  Map,
  Cpu,
  GitBranch,
  Settings,
  HardHat,
  Menu,
  X,
  LogOut,
  ChevronDown,
  Bell,
} from 'lucide-react'

const navigation = [
  { href: '/dashboard', label: 'ダッシュボード', icon: LayoutDashboard },
  { href: '/projects', label: '工事管理', icon: ClipboardList },
  { href: '/documents', label: '文書管理', icon: FileText },
  { href: '/gis', label: 'GIS', icon: Map },
  { href: '/iot', label: 'IoT', icon: Cpu },
  { href: '/workflows', label: 'ワークフロー', icon: GitBranch },
  { href: '/settings', label: '設定', icon: Settings },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Sidebar header */}
        <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6">
          <HardHat className="h-7 w-7 text-primary-600" />
          <span className="text-lg font-bold text-gray-900">CEO-OS</span>
          <button
            className="ml-auto lg:hidden text-gray-500 hover:text-gray-700"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {item.label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Sidebar footer */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-100 text-primary-700 text-sm font-bold">
              TK
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                田中 健一
              </p>
              <p className="text-xs text-gray-500">現場監督</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top header */}
        <header className="flex h-16 items-center gap-4 border-b border-gray-200 bg-white px-4 lg:px-6">
          <button
            className="lg:hidden text-gray-500 hover:text-gray-700"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex-1" />

          <button className="relative text-gray-500 hover:text-gray-700">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-danger-500 text-[10px] font-bold text-white">
              3
            </span>
          </button>

          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-primary-700 text-xs font-bold">
              TK
            </div>
            <span className="hidden sm:inline text-sm font-medium text-gray-700">
              田中 健一
            </span>
            <ChevronDown className="h-4 w-4 text-gray-400" />
          </div>

          <button className="text-gray-400 hover:text-gray-600">
            <LogOut className="h-5 w-5" />
          </button>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
