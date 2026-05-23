import * as React from "react"
import { cn } from "../../lib/utils"

interface TabsContextValue {
  selectedTab: string
  setSelectedTab: (value: string) => void
}

const TabsContext = React.createContext<TabsContextValue>({
  selectedTab: "",
  setSelectedTab: () => {},
})

interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  defaultValue: string
  onValueChange?: (value: string) => void
}

function Tabs({
  defaultValue,
  onValueChange,
  children,
  className,
  ...props
}: TabsProps) {
  const [selectedTab, setSelectedTab] = React.useState(defaultValue)

  const handleChange = React.useCallback(
    (value: string) => {
      setSelectedTab(value)
      onValueChange?.(value)
    },
    [onValueChange]
  )

  return (
    <TabsContext.Provider
      value={{ selectedTab, setSelectedTab: handleChange }}
    >
      <div className={cn(className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}

interface TabsListProps extends React.HTMLAttributes<HTMLDivElement> {}

const TabsList = React.forwardRef<HTMLDivElement, TabsListProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-lg bg-gray-100 p-1 text-gray-500",
        className
      )}
      {...props}
    />
  )
)
TabsList.displayName = "TabsList"

interface TabsTriggerProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string
}

const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ className, value, ...props }, ref) => {
    const { selectedTab, setSelectedTab } = React.useContext(TabsContext)
    const isActive = selectedTab === value

    return (
      <button
        ref={ref}
        type="button"
        role="tab"
        aria-selected={isActive}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500",
          isActive
            ? "bg-white text-gray-900 shadow-sm"
            : "text-gray-500 hover:text-gray-700",
          className
        )}
        onClick={() => setSelectedTab(value)}
        {...props}
      />
    )
  }
)
TabsTrigger.displayName = "TabsTrigger"

interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string
}

const TabsContent = React.forwardRef<HTMLDivElement, TabsContentProps>(
  ({ className, value, ...props }, ref) => {
    const { selectedTab } = React.useContext(TabsContext)
    if (selectedTab !== value) return null

    return (
      <div
        ref={ref}
        role="tabpanel"
        className={cn("mt-2 focus-visible:outline-none", className)}
        {...props}
      />
    )
  }
)
TabsContent.displayName = "TabsContent"

export { Tabs, TabsList, TabsTrigger, TabsContent }
