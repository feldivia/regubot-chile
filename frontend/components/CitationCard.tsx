'use client'

import { ExternalLink, FileText } from 'lucide-react'
import { type Cita } from '@/lib/api'

interface Props {
  cita: Cita
}

export default function CitationCard({ cita }: Props) {
  return (
    <div className="border border-gray-200 rounded-lg p-3 bg-gray-50 hover:bg-gray-100 transition-colors text-sm">
      <div className="flex items-start gap-2">
        <div className="bg-primary-100 text-primary-600 rounded-full w-6 h-6 flex items-center justify-center shrink-0 text-xs font-bold">
          {cita.numero}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-gray-900 truncate">
            {cita.norma} — {cita.titulo}
          </div>
          <div className="text-gray-500 text-xs mt-0.5">
            <FileText size={12} className="inline mr-1" />
            {cita.articulo} | {cita.organismo}
          </div>
          {cita.path && (
            <div className="text-gray-400 text-xs mt-0.5 truncate">
              {cita.path}
            </div>
          )}
        </div>
        {cita.url && (
          <a
            href={cita.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 hover:text-primary-800 shrink-0"
            title="Ver fuente oficial"
          >
            <ExternalLink size={16} />
          </a>
        )}
      </div>
    </div>
  )
}
