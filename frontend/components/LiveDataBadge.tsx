'use client'

import { TrendingUp } from 'lucide-react'

interface Props {
  dato: {
    tipo?: string
    valor?: string
    fecha?: string
    fuente?: string
    [key: string]: unknown
  }
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
  let datoReal = dato
  const keys = Object.keys(dato)
  if (keys.length === 1 && typeof dato[keys[0]] === 'object') {
    datoReal = dato[keys[0]] as typeof dato
  }

  const tipo = datoReal.tipo || keys[0] || 'dato'
  const valor = datoReal.valor || 'N/D'
  const fecha = datoReal.fecha || ''
  const etiqueta = ETIQUETAS[tipo] || tipo.toUpperCase()

  if (datoReal.error) return null

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
