import * as React from "react"
import { cn } from "../../lib/utils"
import { ChevronLeft, ChevronRight } from "lucide-react"
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "../ui/table"

interface DataTableProps<T> {
  columns: {
    key: string
    header: string
    cell?: (item: T) => React.ReactNode
    className?: string
    sortable?: boolean
  }[]
  data: T[]
  keyField: keyof T
  pageSize?: number
  className?: string
  emptyMessage?: string
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  keyField,
  pageSize = 10,
  className,
  emptyMessage = "データがありません",
}: DataTableProps<T>) {
  const [page, setPage] = React.useState(0)
  const totalPages = Math.max(1, Math.ceil(data.length / pageSize))
  const start = page * pageSize
  const pageData = data.slice(start, start + pageSize)

  return (
    <div className={cn("space-y-4", className)}>
      <div className="rounded-lg border border-gray-200 bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead
                  key={col.key}
                  className={cn(
                    col.sortable && "cursor-pointer select-none",
                    col.className
                  )}
                >
                  {col.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {pageData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-gray-500"
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              pageData.map((item) => (
                <TableRow key={String(item[keyField])}>
                  {columns.map((col) => (
                    <TableCell key={col.key} className={col.className}>
                      {col.cell
                        ? col.cell(item)
                        : String(item[col.key] ?? "")}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            {start + 1}-
            {Math.min(start + pageSize, data.length)} / {data.length}件
          </p>
          <div className="flex items-center gap-1">
            <button
              className="inline-flex items-center justify-center h-8 w-8 rounded-md border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                className={cn(
                  "inline-flex items-center justify-center h-8 w-8 rounded-md text-sm font-medium",
                  i === page
                    ? "bg-primary-600 text-white"
                    : "border border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
                )}
                onClick={() => setPage(i)}
              >
                {i + 1}
              </button>
            ))}
            <button
              className="inline-flex items-center justify-center h-8 w-8 rounded-md border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
