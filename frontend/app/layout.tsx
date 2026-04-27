import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ReguBot Chile - Regulación Financiera al Alcance de Todos',
  description:
    'Chatbot con IA que explica la regulación financiera chilena en lenguaje simple, con citas verificadas a fuentes oficiales.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
