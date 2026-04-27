'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Send, Loader2 } from 'lucide-react'
import Message, { type MessageData } from './Message'
import Disclaimer from './Disclaimer'
import { type Cita, type DatoVivo } from '@/lib/api'

const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

interface ChatProps {
  preguntaInicial?: string
  onCitasUpdate?: (citas: Cita[]) => void
}

export default function Chat({ preguntaInicial, onCitasUpdate }: ChatProps) {
  const [messages, setMessages] = useState<MessageData[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => crypto.randomUUID())
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const preguntaInicialEnviada = useRef(false)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const enviarPregunta = useCallback(async (pregunta: string) => {
    if (!pregunta.trim() || isLoading) return

    setInput('')
    setIsLoading(true)

    const userMsg: MessageData = { role: 'user', content: pregunta.trim() }
    setMessages((prev) => [...prev, userMsg])

    const botMsg: MessageData = {
      role: 'assistant',
      content: '',
      citas: [],
      datosVivos: [],
    }
    setMessages((prev) => [...prev, botMsg])

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pregunta: pregunta.trim(), session_id: sessionId }),
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No streaming disponible')

      const decoder = new TextDecoder()
      let buffer = ''
      let textoAcumulado = ''
      const citasAcumuladas: Cita[] = []
      const datosVivosAcumulados: DatoVivo[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEvent = ''
        let dataBuffer = ''

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.slice(6).trim()
            dataBuffer = ''
          } else if (line.startsWith('data:')) {
            // Acumular líneas data: (SSE puede dividir en múltiples líneas)
            const raw = line.slice(5)
            dataBuffer += (dataBuffer ? '\n' : '') + (raw.startsWith(' ') ? raw.slice(1) : raw)
          } else if (line.trim() === '' && dataBuffer) {
            // Línea vacía = fin del evento SSE, procesar
            let contenido: string
            try {
              contenido = JSON.parse(dataBuffer)
            } catch {
              contenido = dataBuffer
            }

            if (currentEvent === 'texto') {
              textoAcumulado += contenido
              setMessages((prev) => {
                const updated = [...prev]
                const last = updated[updated.length - 1]
                if (last.role === 'assistant') {
                  last.content = textoAcumulado
                }
                return [...updated]
              })
            } else if (currentEvent === 'cita') {
              try {
                const cita = typeof contenido === 'string' ? JSON.parse(contenido) : contenido
                citasAcumuladas.push(cita)
                setMessages((prev) => {
                  const updated = [...prev]
                  const last = updated[updated.length - 1]
                  if (last.role === 'assistant') {
                    last.citas = [...citasAcumuladas]
                  }
                  return [...updated]
                })
                onCitasUpdate?.([...citasAcumuladas])
              } catch {
                // Cita no parseable
              }
            } else if (currentEvent === 'dato_vivo') {
              try {
                const raw = typeof contenido === 'string' ? JSON.parse(contenido) : contenido
                const keys = Object.keys(raw)
                if (keys.length === 1 && typeof raw[keys[0]] === 'object') {
                  const inner = raw[keys[0]] as DatoVivo
                  if (inner.valor) datosVivosAcumulados.push(inner)
                }
                setMessages((prev) => {
                  const updated = [...prev]
                  const last = updated[updated.length - 1]
                  if (last.role === 'assistant') {
                    last.datosVivos = [...datosVivosAcumulados]
                  }
                  return [...updated]
                })
              } catch {
                // Dato no parseable
              }
            } else if (currentEvent === 'error') {
              textoAcumulado += `\n\nError: ${contenido}`
              setMessages((prev) => {
                const updated = [...prev]
                const last = updated[updated.length - 1]
                if (last.role === 'assistant') {
                  last.content = textoAcumulado
                }
                return [...updated]
              })
            }

            dataBuffer = ''
          }
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last.role === 'assistant') {
          last.content =
            'Lo siento, hubo un error al procesar tu consulta. Por favor, intenta de nuevo.'
        }
        return [...updated]
      })
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, sessionId, onCitasUpdate])

  // Enviar pregunta inicial automáticamente
  useEffect(() => {
    if (preguntaInicial && !preguntaInicialEnviada.current) {
      preguntaInicialEnviada.current = true
      enviarPregunta(preguntaInicial)
    }
  }, [preguntaInicial, enviarPregunta])

  const handleSubmit = () => {
    enviarPregunta(input)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Mensajes */}
      <div className="flex-1 overflow-y-auto chat-scroll px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 text-sm">
              Escribe tu pregunta sobre regulación financiera chilena
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} message={msg} isStreaming={isLoading && i === messages.length - 1 && msg.role === 'assistant'} />
        ))}

        {isLoading && messages[messages.length - 1]?.content === '' && (
          <div className="chat-bubble-bot inline-flex gap-1 py-4">
            <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full" />
            <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full" />
            <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full" />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Disclaimer */}
      <div className="px-4 py-1">
        <Disclaimer compact />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-200/60 bg-white/80 backdrop-blur-md">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pregunta sobre regulación financiera..."
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-400 transition-all placeholder:text-slate-400"
            disabled={isLoading}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-3 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm shadow-primary-500/20"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
