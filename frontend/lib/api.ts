const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

export interface ChatEvent {
  tipo: 'texto' | 'cita' | 'dato_vivo' | 'verificacion' | 'error' | 'fin'
  contenido: string
}

export interface Cita {
  numero: number
  norma: string
  titulo: string
  articulo: string
  path: string
  url: string
  organismo: string
  texto?: string
}

export interface DatoVivo {
  tipo: string
  valor: string
  fecha: string
  fuente: string
}

export async function* enviarPregunta(
  pregunta: string,
  sessionId?: string
): AsyncGenerator<ChatEvent> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      pregunta,
      session_id: sessionId,
    }),
  })

  if (!response.ok) {
    yield { tipo: 'error', contenido: `Error ${response.status}: ${response.statusText}` }
    return
  }

  const reader = response.body?.getReader()
  if (!reader) {
    yield { tipo: 'error', contenido: 'No se pudo iniciar streaming' }
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('event:')) {
        const eventType = line.slice(6).trim()
        continue
      }
      if (line.startsWith('data:')) {
        const data = line.slice(5).trim()
        if (!data) continue

        // Parsear evento SSE
        try {
          yield { tipo: 'texto', contenido: data }
        } catch {
          yield { tipo: 'texto', contenido: data }
        }
      }
    }
  }
}
