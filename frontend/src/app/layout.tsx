import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Financial Research Assistant',
  description: 'AI-powered financial analysis and research tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
} 