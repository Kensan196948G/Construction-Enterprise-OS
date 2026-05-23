import * as React from "react"
import { cn } from "../../lib/utils"
import { ArrowDown, ArrowUp } from "lucide-react"

interface StatCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string
  value: string | number
  icon?: React.ReactNode
  trend?: string
  trendDirection?: "up" | "down"
  color?: "primary" | "safety" | "danger" | "approve" | "site" | "concrete"
}

const colorMap = {
  primary: {
    bg: "bg-primary-50",
    icon: "text-primary-600",
    text: "text-primary-700",
  },
  safety: {
    bg: "bg-safety-50",
    icon: "text-safety-500",
    text: "text-safety-700",
  },
  danger: {
    bg: "bg-danger-50",
    icon: "text-danger-500",
    text: "text-danger-700",
  },
  approve: {
    bg: "bg-approve-50",
    icon: "text-approve-500",
    text: "text-approve-700",
  },
  site: {
    bg: "bg-site-50",
    icon: "text-site-500",
    text: "text-site-700",
  },
  concrete: {
    bg: "bg-concrete-50",
    icon: "text-concrete-500",
    text: "text-concrete-700",
  },
}

export function StatCard({
  label,
  value,
  icon,
  trend,
  trendDirection = "up",
  color = "primary",
  className,
  ...props
}: StatCardProps) {
  const colors = colorMap[color]
  const TrendIcon = trendDirection === "up" ? ArrowUp : ArrowDown
  const trendColor = trendDirection === "up" ? "text-approve-600" : "text-danger-600"

  return (
    <div
      className={cn(
        "rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md transition-shadow",
        className
      )}
      {...props}
    >
      <div className="flex items-start justify-between">
        {icon && (
          <div className={cn("rounded-lg p-2.5", colors.bg)}>
            <div className={cn("h-5 w-5", colors.icon)}>{icon}</div>
          </div>
        )}
      </div>
      <p className="mt-4 text-3xl font-bold text-gray-900">{value}</p>
      <p className="mt-1 text-sm font-medium text-gray-600">{label}</p>
      {trend && (
        <div className="mt-2 flex items-center gap-1">
          <TrendIcon className={cn("h-3 w-3", trendColor)} />
          <p className={cn("text-xs font-medium", trendColor)}>{trend}</p>
        </div>
      )}
    </div>
  )
}
