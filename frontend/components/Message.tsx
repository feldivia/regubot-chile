'use client'

import { Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
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
      {/* Avatar bot */}
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

        {/* Indicador de citas (sin tarjetas, van al panel) */}
        {!isStreaming && message.citas && message.citas.length > 0 && (
          <div className="flex items-center gap-1.5 text-xs text-primary-600">
            <span className="font-medium">
              {message.citas.length} fuente{message.citas.length > 1 ? 's' : ''} citada{message.citas.length > 1 ? 's' : ''}
            </span>
            <span className="text-gray-400">— ver panel de fuentes</span>
          </div>
        )}
      </div>

      {/* Avatar usuario */}
      {isUser && (
        <div className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-primary-600 text-white mt-1">
          <User size={16} />
        </div>
      )}
    </div>
  )
}
