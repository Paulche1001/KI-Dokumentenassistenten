import { useEffect, useState } from 'react'
import { checkHealth } from './api/health'
import DocumentUpload from './components/DocumentUpload'

type Connection = 'loading' | 'connected' | 'error'

export default function App() {
  const [connection, setConnection] = useState<Connection>('loading')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 5000)
    let active = true
    setConnection('loading')

    checkHealth(controller.signal)
      .then(() => { if (active) setConnection('connected') })
      .catch(() => { if (active) setConnection('error') })
      .finally(() => window.clearTimeout(timeout))

    return () => {
      active = false
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [attempt])

  const message = {
    loading: 'Verbindung wird geprüft ...',
    connected: 'Backend verbunden',
    error: 'Backend nicht erreichbar. Starte FastAPI und prüfe die Verbindung erneut.',
  }[connection]

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
      <div className="mx-auto max-w-2xl">
        <p className="text-sm font-semibold tracking-wide text-teal-700">Lernprojekt / Schritt 2</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight">KI-Dokumentenassistent</h1>
        <p className="mt-5 text-lg leading-relaxed text-slate-600">
          Hier entsteht Schritt für Schritt ein Assistent, der Fragen zu deinen PDF-Dokumenten beantwortet.
        </p>
        <section aria-labelledby="connection-heading" className="mt-10 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 id="connection-heading" className="text-xl font-semibold">Verbindung zum Backend</h2>
          <p role="status" className={`mt-3 ${connection === 'error' ? 'text-red-700' : connection === 'connected' ? 'text-teal-700' : 'text-slate-600'}`}>
            {message}
          </p>
          <button
            type="button"
            disabled={connection === 'loading'}
            onClick={() => setAttempt(value => value + 1)}
            className="mt-6 rounded-lg bg-teal-700 px-4 py-2 font-medium text-white hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-700 disabled:cursor-wait disabled:opacity-50"
          >
            Verbindung prüfen
          </button>
        </section>
        <DocumentUpload />
      </div>
    </main>
  )
}
