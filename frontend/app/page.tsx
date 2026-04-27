'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import CitasPanel from '@/components/CitasPanel'
import Disclaimer from '@/components/Disclaimer'
import { type Cita } from '@/lib/api'
import { Scale, BookOpen, Sparkles } from 'lucide-react'

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
    <main className="h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-4 py-3 shrink-0 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-primary-500 to-primary-700 text-white p-2 rounded-xl shadow-md shadow-primary-500/20">
              <Scale size={22} />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 tracking-tight">ReguBot Chile</h1>
              <p className="text-xs text-slate-500">
                Regulación financiera al alcance de todos
              </p>
            </div>
          </div>

          {/* Botón fuentes - solo mobile */}
          {chatIniciado && (
            <button
              onClick={() => setPanelAbierto(!panelAbierto)}
              className="lg:hidden flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors text-sm text-slate-600"
            >
              <BookOpen size={16} />
              {todasLasCitas.length > 0 && (
                <span className="bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
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
                <div className="relative inline-block mb-8">
                  <div className="bg-gradient-to-br from-primary-100 to-primary-200 text-primary-600 p-5 rounded-2xl shadow-lg shadow-primary-500/10">
                    <Scale size={44} />
                  </div>
                  <div className="absolute -top-1 -right-1 bg-gradient-to-br from-amber-400 to-amber-500 text-white p-1 rounded-lg shadow-sm">
                    <Sparkles size={14} />
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-3 tracking-tight">
                  Pregunta sobre regulación financiera
                </h2>
                <p className="text-slate-500 mb-10 text-base leading-relaxed">
                  Explico leyes financieras chilenas en lenguaje simple, con
                  citas verificadas. Tengo información sobre derechos del
                  consumidor, tasas de interés, Ley Fintec, mercado de valores
                  y sistemas de pago.
                </p>

                {/* Sugerencias */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-10">
                  {SUGERENCIAS.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => iniciarConPregunta(s)}
                      className="text-left p-4 rounded-xl border border-slate-200 hover:border-primary-300 hover:bg-primary-50/50 hover:shadow-sm transition-all text-sm text-slate-600 hover:text-slate-900"
                    >
                      <span className="text-primary-500 mr-2">→</span>
                      {s}
                    </button>
                  ))}
                </div>

                <Disclaimer />
              </div>
            </div>

            <div className="p-4 pb-6">
              <div className="max-w-2xl mx-auto">
                <input
                  type="text"
                  placeholder="Escribe tu pregunta sobre regulación financiera..."
                  className="w-full px-5 py-3.5 rounded-xl border border-slate-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-400 transition-all placeholder:text-slate-400"
                  onFocus={() => setChatIniciado(true)}
                />
              </div>
            </div>
          </div>
        ) : (
          /* Chat + Panel lateral */
          <>
            <div className="flex-1 flex flex-col min-w-0">
              <Chat
                preguntaInicial={preguntaInicial}
                onCitasUpdate={handleCitasUpdate}
              />
            </div>

            {/* Panel lateral - siempre visible en desktop */}
            <div className="hidden lg:block w-80 shrink-0 bg-white/50 backdrop-blur-sm border-l border-slate-200/60">
              <CitasPanel
                citas={todasLasCitas}
                onClose={() => {}}
              />
            </div>

            {/* Panel mobile - overlay */}
            {panelAbierto && (
              <>
                <div
                  className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 lg:hidden"
                  onClick={() => setPanelAbierto(false)}
                />
                <div className="fixed right-0 top-0 bottom-0 w-80 bg-white shadow-2xl z-50 lg:hidden">
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
  '¿Qué cláusulas son abusivas en un contrato de adhesión?',
  '¿Qué es la Ley Fintec y el sistema de finanzas abiertas?',
  '¿Qué es información privilegiada en el mercado de valores?',
]
