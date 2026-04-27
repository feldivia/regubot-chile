'use client'

import { BookOpen, ExternalLink, FileText, X } from 'lucide-react'
import { type Cita } from '@/lib/api'

interface Props {
  citas: Cita[]
  onClose: () => void
}

export default function CitasPanel({ citas, onClose }: Props) {
  if (citas.length === 0) {
    return (
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <BookOpen size={18} className="text-primary-600" />
            <h2 className="font-semibold text-gray-900 text-sm">Fuentes citadas</h2>
          </div>
          <button onClick={onClose} className="lg:hidden text-gray-400 hover:text-gray-600">
            <X size={18} />
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <p className="text-gray-400 text-sm text-center">
            Las fuentes normativas aparecerán aquí cuando el chatbot cite artículos de ley.
          </p>
        </div>
      </div>
    )
  }

  // Agrupar citas por norma
  const porNorma = citas.reduce<Record<string, Cita[]>>((acc, cita) => {
    const key = `${cita.norma}`
    if (!acc[key]) acc[key] = []
    // Evitar duplicados por articulo_id
    if (!acc[key].some((c) => c.articulo === cita.articulo && c.norma === cita.norma)) {
      acc[key].push(cita)
    }
    return acc
  }, {})

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <BookOpen size={18} className="text-primary-600" />
          <h2 className="font-semibold text-gray-900 text-sm">
            Fuentes citadas ({citas.length})
          </h2>
        </div>
        <button onClick={onClose} className="lg:hidden text-gray-400 hover:text-gray-600">
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {Object.entries(porNorma).map(([norma, citasNorma]) => (
          <div key={norma} className="space-y-2">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              {norma}
            </h3>
            {citasNorma.map((cita, i) => (
              <div
                key={i}
                className="bg-white border border-gray-200 rounded-lg p-3 hover:border-primary-300 transition-colors"
              >
                <div className="flex items-start gap-2">
                  <div className="bg-primary-100 text-primary-700 rounded-full w-6 h-6 flex items-center justify-center shrink-0 text-xs font-bold mt-0.5">
                    {cita.numero}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 text-sm">
                      Art. {cita.articulo}
                    </div>
                    {cita.path && (
                      <div className="text-gray-500 text-xs mt-0.5 flex items-center gap-1">
                        <FileText size={10} />
                        {cita.path}
                      </div>
                    )}
                    <div className="text-gray-400 text-xs mt-0.5">
                      {cita.organismo}
                    </div>
                  </div>
                  {cita.url && (
                    <a
                      href={cita.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-800 shrink-0"
                      title="Ver fuente oficial"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
