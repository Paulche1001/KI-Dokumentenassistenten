import { useState } from 'react'
import type { FormEvent } from 'react'
import { extractDocument } from '../api/documents'
import type { DocumentExtraction } from '../types/documents'

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<DocumentExtraction | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file || loading) return
    setError('')
    setResult(null)
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Bitte wähle eine PDF-Datei aus.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('Das PDF darf höchstens 10 MiB groß sein.')
      return
    }

    setLoading(true)
    try {
      setResult(await extractDocument(file))
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Der Upload ist fehlgeschlagen.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section aria-labelledby="upload-heading" className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 id="upload-heading" className="text-xl font-semibold">PDF untersuchen</h2>
      <p id="upload-help" className="mt-3 text-slate-600">
        Lade ein PDF mit auswählbarem Text hoch (max. 10 MiB und 200 Seiten).
        Du erhältst eine Textvorschau pro Seite. Das Dokument wird nicht dauerhaft gespeichert.
      </p>
      <form onSubmit={handleSubmit} className="mt-6">
        <label htmlFor="pdf-file" className="block font-medium">PDF-Datei auswählen</label>
        <input
          id="pdf-file"
          type="file"
          accept=".pdf,application/pdf"
          aria-describedby="upload-help"
          disabled={loading}
          onChange={event => {
            setFile(event.target.files?.[0] ?? null)
            setResult(null)
            setError('')
          }}
          className="mt-2 block w-full min-w-0 rounded-lg border border-slate-300 p-2 text-sm file:mr-3 file:rounded file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-slate-700"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="mt-4 rounded-lg bg-teal-700 px-4 py-2 font-medium text-white hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Text wird extrahiert …' : 'Text extrahieren'}
        </button>
      </form>
      {loading && <p role="status" className="mt-4 text-slate-600">Das PDF wird hochgeladen und gelesen …</p>}
      {error && <p role="alert" className="mt-4 text-red-700">{error}</p>}
      {result && (
        <div className="mt-6">
          <p role="status" className="break-words font-medium text-teal-700">
            {result.filename}: {result.page_count} Seite(n) verarbeitet.
          </p>
          {result.warnings.map(warning => (
            <p key={warning} className="mt-3 text-amber-800">{warning}</p>
          ))}
          <div className="mt-4 max-h-[36rem] space-y-3 overflow-y-auto">
            {result.pages.map(page => (
              <details key={page.page_number} open={page.page_number === 1} className="rounded-lg border border-slate-200 p-4">
                <summary className="cursor-pointer font-medium">Seite {page.page_number}</summary>
                <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-relaxed text-slate-700">
                  {page.text || 'Kein auslesbarer Text auf dieser Seite.'}
                </p>
              </details>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
