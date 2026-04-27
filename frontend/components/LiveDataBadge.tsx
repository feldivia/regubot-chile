'use client'

import { TrendingUp } from 'lucide-react'
import { type DatoVivo } from '@/lib/api'

interface Props {
  dato: DatoVivo
}

const ETIQUETAS: Record<string, string> = {
  uf: 'UF',
  utm: 'UTM',
  tpm: 'TPM',
  tmc: 'TMC',
  dolar: 'Dólar',
  ipc: 'IPC',
  sueldo_minimo: 'Sueldo Mínimo',
}

export default function LiveDataBadge({ dato }: Props) {
  // El dato puede venir anidado (ej: {uf: {tipo, valor, ...}})
  const tipo = dato.tipo || 'dato'
  const valor = dato.valor || 'N/D'
  const fecha = dato.fecha || ''
  const etiqueta = ETIQUETAS[tipo] || tipo.toUpperCase()

  if (!dato.valor) return null

  return (
    <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-1.5 text-sm">
      <TrendingUp size={14} className="text-green-600" />
      <span className="font-medium text-green-800">
        {etiqueta}: ${valor}
      </span>
      {fecha && (
        <span className="text-green-600 text-xs">({fecha})</span>
      )}
    </div>
  )
}
