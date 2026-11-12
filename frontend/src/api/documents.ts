import { isDocumentExtraction } from '../types/documents'
import type { DocumentExtraction } from '../types/documents'

export async function extractDocument(file: File): Promise<DocumentExtraction> {
  const form = new FormData()
  form.append('file', file)

  let response: Response
  try {
    // Den Content-Type mit Multipart-Grenze setzt der Browser selbst.
    response = await fetch('/api/documents/extract', {
      method: 'POST',
      body: form,
      signal: AbortSignal.timeout(60_000),
    })
  } catch {
    throw new Error('Keine Antwort vom Backend erhalten. Prüfe die Verbindung und versuche es erneut.')
  }

  const data: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    if (typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string') {
      throw new Error(data.detail)
    }
    throw new Error(`Upload fehlgeschlagen (HTTP ${response.status}).`)
  }
  if (!isDocumentExtraction(data)) {
    throw new Error('Das Backend hat ein unerwartetes Antwortformat geliefert.')
  }
  return data
}
