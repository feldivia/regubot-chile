'use client'

import { AlertTriangle } from 'lucide-react'

interface Props {
  compact?: boolean
}

export default function Disclaimer({ compact }: Props) {
  if (compact) {
    return (
      <p className="text-xs text-gray-400 text-center">
        <AlertTriangle size={10} className="inline mr-1" />
        Información orientativa, no constituye asesoría legal.{' '}
        <a
          href="https://www.sernac.cl"
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-gray-600"
        >
          SERNAC
        </a>
      </p>
    )
  }

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
      <div className="flex items-start gap-2">
        <AlertTriangle size={18} className="shrink-0 mt-0.5 text-amber-600" />
        <div>
          <p className="font-medium mb-1">Aviso importante</p>
          <p>
            ReguBot proporciona información orientativa sobre regulación
            financiera chilena. <strong>No constituye asesoría legal.</strong>{' '}
            Para decisiones financieras importantes o disputas, consulta a un
            abogado o acude a{' '}
            <a
              href="https://www.sernac.cl"
              target="_blank"
              rel="noopener noreferrer"
              className="underline font-medium hover:text-amber-900"
            >
              SERNAC
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  )
}
