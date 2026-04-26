'use client'

import { Bot, User } from 'lucide-react'
import CitationCard from './CitationCard'
import LiveDataBadge from './LiveDataBadge'
import { type Cita, type DatoVivo } from '@/lib/api'

export interface MessageData {
  role: 'user' | 'assistant'
  content: string
  citas?: Cita[]
  datosVivos?: DatoVivo[]
}

interface Props {
  message: MessageData
  isStreaming?: boolean
}

export default function Message({ message, isStreaming }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
        }`}
      >
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Contenido */}
      <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={isUser ? 'chat-bubble-user' : 'chat-bubble-bot'}>
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
            {isStreaming && <span className="animate-pulse">|</span>}
          </div>
        </div>

        {/* Datos en vivo */}
        {message.datosVivos && message.datosVivos.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.datosVivos.map((dato, i) => (
              <LiveDataBadge key={i} dato={dato} />
            ))}
          </div>
        )}

        {/* Citas */}
        {message.citas && message.citas.length > 0 && (
          <div className="space-y-2 w-full max-w-md">
            {message.citas.map((cita, i) => (
              <CitationCard key={i} cita={cita} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
