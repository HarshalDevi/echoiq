import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'EchoIQ',
  description: 'Upload audio to transcribe, summarize and analyze instantly.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`min-h-screen w-full bg-gradient-animation ${inter.className}`}>
        <main className="flex items-center justify-center min-h-screen">
          <div className="glass p-10 max-w-xl w-full text-white text-center space-y-4">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}
