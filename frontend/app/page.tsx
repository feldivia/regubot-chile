'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import Disclaimer from '@/components/Disclaimer'
import { Scale } from 'lucide-react'

export default function Home() {
  const [chatIniciado, setChatIniciado] = useState(false)

  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="bg-primary-600 text-white p-2 rounded-lg">
            <Scale size={24} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">ReguBot Chile</h1>
            <p className="text-xs text-gray-500">
              Regulación financiera al alcance de todos
            </p>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {!chatIniciado ? (
          <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
            <div className="text-center max-w-2xl">
              <div className="bg-primary-100 text-primary-600 p-4 rounded-full inline-block mb-6">
                <Scale size={48} />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Pregunta sobre regulación financiera chilena
              </h2>
              <p className="text-gray-600 mb-8">
                Explico leyes financieras en lenguaje simple, con citas
                verificadas a fuentes oficiales. Puedo ayudarte con la Ley del
                Consumidor, Ley Fintec, Mercado de Valores, Operaciones de
                Crédito y Sistemas de Pago.
              </p>

              {/* Sugerencias */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
                {SUGERENCIAS.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => setChatIniciado(true)}
                    className="text-left p-3 rounded-xl border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-sm text-gray-700"
                  >
                    {s}
                  </button>
                ))}
              </div>

              <Disclaimer />
            </div>
          </div>
        ) : (
          <Chat />
        )}

        {!chatIniciado && (
          <div className="p-4">
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Escribe tu pregunta sobre regulación financiera..."
                  className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  onFocus={() => setChatIniciado(true)}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

const SUGERENCIAS = [
  '¿Qué derechos tengo como consumidor?',
  '¿Cuál es la tasa máxima de interés que me pueden cobrar?',
  '¿Qué es la Ley Fintec y el sistema de finanzas abiertas?',
  '¿Qué es información privilegiada en el mercado de valores?',
]
