'use client'

import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
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

function limpiarCitas(texto: string): string {
  return texto.replace(/\[CITA:[a-f0-9-]+\]/g, '')
}

export default function Message({ message, isStreaming }: Props) {
  const isUser = message.role === 'user'
  const contenidoLimpio = isUser ? message.content : limpiarCitas(message.content)

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Avatar bot (izquierda) */}
      {!isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 text-gray-600 mt-1">
          <Bot size={16} />
        </div>
      )}

      {/* Contenido */}
      <div className={`flex flex-col gap-2 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={isUser ? 'chat-bubble-user' : 'chat-bubble-bot'}>
          {isUser ? (
            <div className="text-sm leading-relaxed">{message.content}</div>
          ) : (
            <div className="prose-chat text-sm leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {contenidoLimpio}
              </ReactMarkdown>
              {isStreaming && <span className="inline-block w-1.5 h-4 bg-primary-500 animate-pulse ml-0.5 align-text-bottom rounded-sm" />}
            </div>
          )}
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
          <div className="space-y-2 w-full">
            <p className="text-xs text-gray-500 font-medium mt-1">Fuentes consultadas:</p>
            {message.citas.map((cita, i) => (
              <CitationCard key={i} cita={cita} />
            ))}
          </div>
        )}
      </div>

      {/* Avatar usuario (derecha) */}
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-primary-600 text-white mt-1">
          <User size={16} />
        </div>
      )}
    </div>
  )
}
