# KI-Dokumentenassistent

Lern- und Portfolio-Projekt mit React, TypeScript, Tailwind CSS und FastAPI.
Aktueller Stand: Schritt 1, Frontend mit Backend-Statusanzeige.

## Voraussetzungen

- Python 3.11 oder neuer (hier mit Python 3.11.3 eingerichtet)
- Node.js 24 LTS mit npm (hier Node 24.11.1)
- Zwei PowerShell-Terminals im Projektordner

## Einmalige Installation

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Frontend (zweites Terminal, vom Projektordner aus):

```powershell
cd frontend
npm.cmd install
```

Die Python-Umgebung wird direkt aufgerufen. Eine Aktivierung und eine Anpassung der PowerShell-Ausführungsrichtlinie sind nicht erforderlich.
`npm.cmd` funktioniert auch, wenn PowerShell das Skript `npm.ps1` blockiert.

## Starten

Terminal 1, im Ordner `backend`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, im Ordner `frontend`:

```powershell
npm.cmd run dev
```

Frontend: http://127.0.0.1:5173
Backend-Status: http://127.0.0.1:8000/api/health
Interaktive API-Dokumentation: http://127.0.0.1:8000/docs

Erwartete API-Antwort: `{"status":"ok"}`.
Die Oberfläche zeigt nach dem Start beider Server "Backend verbunden".
Beide Server lassen sich im jeweiligen Terminal mit Strg+C stoppen.

## Den ersten Anfrageweg verstehen

1. `frontend/src/main.tsx` bindet React in das HTML-Element `root` ein.
2. `frontend/src/App.tsx` zeigt die Seite. `useEffect` startet beim Laden eine Statusabfrage; `useState` speichert deren Ergebnis.
3. `frontend/src/api/health.ts` sendet mit `fetch` eine HTTP-GET-Anfrage an `/api/health` und prüft die Antwort auch zur Laufzeit.
4. `frontend/vite.config.ts` leitet diese Anfrage während der Entwicklung an Port 8000 weiter. Dadurch braucht dieser lokale Ablauf keine CORS-Konfiguration.
5. In `backend/app/main.py` verbindet `@app.get` den URL-Pfad mit der Python-Funktion `health`. FastAPI gibt deren Ergebnis als JSON zurück.
6. React aktualisiert die Statusanzeige. Nach fuenf Sekunden ohne Antwort erscheint eine Fehlermeldung; der Knopf startet einen neuen Versuch.

Der Vite-Proxy gilt nur für den Entwicklungsserver. Ein späteres Deployment braucht eine eigene Weiterleitung für `/api`.
Der Health-Endpunkt prüft nur die Erreichbarkeit der API; Ollama und Datenbank sind noch nicht angebunden.

## Selbst ausprobieren

- Backend stoppen und auf "Verbindung prüfen" klicken: Es sollte eine Fehlermeldung erscheinen.
- Backend wieder starten und erneut prüfen: Es sollte "Backend verbunden" erscheinen.
- Im Browser die Entwicklerwerkzeuge öffnen: Unter Netzwerk ist die Anfrage an `/api/health` sichtbar.
- Unter `/docs` den GET-Endpunkt selbst ausführen.

## Pruefen

Im Frontend-Ordner:

```powershell
npm.cmd run build
```

Das prüft TypeScript und erzeugt den Produktionsbuild in `dist/`.

## Nächster Schritt

Schritt 2: PDF-Upload und seitenweise Textextraktion mit PyMuPDF.
RAG, Embeddings und Ollama folgen in späteren Schritten.

## Dokumentation

- Vite: https://vite.dev/guide/
- Tailwind mit Vite: https://tailwindcss.com/docs/installation/using-vite
- FastAPI: https://fastapi.tiangolo.com/tutorial/first-steps/

## Entwicklung mit Git und GitHub

Git speichert lokale Entwicklungsstaende als Commits. `git push` uebertraegt
sie in das GitHub-Repository. Wir erstellen nach jedem abgeschlossenen und
geprueften Lernschritt einen Commit mit einer aussagekraeftigen Nachricht.

Alle Befehle werden im Projektordner ausgefuehrt:

```powershell
git status
git diff
# Nur die Dateien des abgeschlossenen Schritts aufnehmen, zum Beispiel:
git add backend/app/main.py README.md
git diff --cached
git commit -m "Describe the completed change"
git push
```

`git diff --cached` zeigt vor dem Commit genau die vorgemerkten Aenderungen.
Vor dem ersten Push muss ein GitHub-Repository als `origin` verbunden sein;
`git push -u origin main` setzt die Zuordnung fuer spaetere Aufrufe von `git push`.
Bei einem neuen Klon installiert man die Frontend-Abhaengigkeiten mit `npm.cmd ci`
aus der eingecheckten `package-lock.json`.

Die `.gitignore` schliesst virtuelle Python-Umgebungen, `node_modules`, Builds,
lokale `.env`-Dateien und den Ordner `data/` aus. Dokumente gehoeren in `data/`.
