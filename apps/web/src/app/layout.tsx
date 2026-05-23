import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CEO-OS | 建設業統合OS',
  description:
    'Construction Enterprise Operating System - 建設・土木業界向け統合業務プラットフォーム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="font-sans min-h-screen bg-gray-50 antialiased">
        {children}
      </body>
    </html>
  )
}
