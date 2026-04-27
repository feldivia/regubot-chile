'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import CitasPanel from '@/components/CitasPanel'
import Disclaimer from '@/components/Disclaimer'
import { type Cita } from '@/lib/api'
import { Scale, BookOpen } from 'lucide-react'

export default function Home() {
  const [chatIniciado, setChatIniciado] = useState(false)
  const [preguntaInicial, setPreguntaInicial] = useState<string | undefined>()
  const [todasLasCitas, setTodasLasCitas] = useState<Cita[]>([])
  const [panelAbierto, setPanelAbierto] = useState(false)

  const iniciarConPregunta = (pregunta: string) => {
    setPreguntaInicial(pregunta)
    setChatIniciado(true)
  }

  const handleCitasUpdate = (citas: Cita[]) => {
    setTodasLasCitas((prev) => {
      const nuevas = citas.filter(
        (c) => !prev.some((p) => p.articulo === c.articulo && p.norma === c.norma)
      )
      if (nuevas.length === 0) return prev
      return [...prev, ...nuevas]
    })
  }

  return (
    <main className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 shrink-0">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
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

          {/* Botón panel de citas (mobile + desktop) */}
          {chatIniciado && (
            <button
              onClick={() => setPanelAbierto(!panelAbierto)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-sm text-gray-700"
            >
              <BookOpen size={16} />
              <span className="hidden sm:inline">Fuentes</span>
              {todasLasCitas.length > 0 && (
                <span className="bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {todasLasCitas.length}
                </span>
              )}
            </button>
          )}
        </div>
      </header>

      {/* Contenido */}
      <div className="flex-1 flex min-h-0">
        {!chatIniciado ? (
          /* Landing */
          <div className="flex-1 flex flex-col">
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
                      onClick={() => iniciarConPregunta(s)}
                      className="text-left p-3 rounded-xl border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors text-sm text-gray-700"
                    >
                      {s}
                    </button>
                  ))}
                </div>

                <Disclaimer />
              </div>
            </div>

            <div className="p-4">
              <div className="max-w-2xl mx-auto">
                <input
                  type="text"
                  placeholder="Escribe tu pregunta sobre regulación financiera..."
                  className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  onFocus={() => setChatIniciado(true)}
                />
              </div>
            </div>
          </div>
        ) : (
          /* Chat + Panel lateral */
          <>
            {/* Chat principal */}
            <div className="flex-1 flex flex-col min-w-0">
              <Chat
                preguntaInicial={preguntaInicial}
                onCitasUpdate={handleCitasUpdate}
              />
            </div>

            {/* Panel lateral de citas */}
            {panelAbierto && (
              <>
                {/* Overlay mobile */}
                <div
                  className="fixed inset-0 bg-black/30 z-40 lg:hidden"
                  onClick={() => setPanelAbierto(false)}
                />
                {/* Panel */}
                <div className="fixed right-0 top-0 bottom-0 w-80 bg-gray-50 border-l border-gray-200 z-50 lg:static lg:z-auto lg:w-80 lg:shrink-0">
                  <CitasPanel
                    citas={todasLasCitas}
                    onClose={() => setPanelAbierto(false)}
                  />
                </div>
              </>
            )}
          </>
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
