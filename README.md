# KI-Dokumentenassistent

Lern- und Portfolio-Projekt mit React, TypeScript, Tailwind CSS und FastAPI.
Aktueller Stand: Schritt 2, PDF-Upload mit seitenweiser Textvorschau und Backend-Statusanzeige.

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

Im Backend-Ordner (HTTPX wird nur für die Tests benötigt):

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Die Tests erzeugen PDFs im Speicher und prüfen Text und Seitennummern,
leere Seiten, Passwortschutz, falsche Dateien sowie Größen- und Seitenlimits.

Im Frontend-Ordner:

```powershell
npm.cmd run build
```

Das prüft TypeScript und erzeugt den Produktionsbuild in `dist/`.

## Nächster Schritt

Schritt 3: Text in sinnvolle Abschnitte aufteilen (Chunking), mit Seitennummern.
RAG, Embeddings und Ollama folgen in späteren Schritten.

## Schritt 2 verstehen: vom PDF zum Text

Wenn du Schritt 1 bereits installiert hast, installiere die neuen Backend-Abhängigkeiten
im Ordner `backend` mit `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`.
Starte das Backend anschließend neu. Das Frontend startest du wie oben mit `npm.cmd run dev`.

```text
DocumentUpload.tsx → FormData → POST /api/documents/extract
                  → API-Router → extract_pdf → JSON → Textvorschau
```

1. `frontend/src/components/DocumentUpload.tsx` enthält das Formular und speichert
   Dateiauswahl, Ladezustand, Fehlermeldung und Ergebnis mit `useState`.
2. `frontend/src/api/documents.ts` verpackt die Datei mit `FormData` als
   `multipart/form-data`. Der Browser setzt den passenden Content-Type inklusive
   Trennmarkierung. Wir setzen diesen Header deshalb nicht selbst.
3. `backend/app/api/documents.py` nimmt die Datei als `UploadFile` an und prüft
   Endung, leeren Inhalt und das Größenlimit von 10 MiB. Die synchrone Route läuft
   in FastAPIs Threadpool, damit die PDF-Verarbeitung nicht die Async-Ereignisschleife blockiert.
4. `backend/app/services/pdf.py` öffnet die Bytes mit PyMuPDF und prüft den tatsächlichen
   Dokumenttyp. `page.get_text("text", sort=True)` liest den Text pro Seite mit einer
   geometrisch sortierten Lesereihenfolge. Komplexe Spalten und Tabellen können dennoch
   Nacharbeit erfordern. Ein PDF darf in diesem Schritt höchstens 200 Seiten haben.
5. `backend/app/schemas/documents.py` beschreibt das JSON-Antwortformat mit Pydantic.
   Die PDF-Seiten zählen wir für die Anzeige ab 1. Auch leere Seiten bleiben erhalten,
   damit die späteren Quellenangaben stimmen. Die Nummer meint die physische PDF-Seite,
   nicht eine eventuell abweichende gedruckte Seitenzahl.
6. Das Frontend prüft das Antwortformat zur Laufzeit und zeigt Text pro Seite an.
   TypeScript-Typen allein prüfen keine vom Netzwerk empfangenen Daten.

Es wird noch kein Dokument dauerhaft gespeichert. FastAPI kann Uploads während der
Anfrage in einer temporären Datei zwischenspeichern; diese wird anschließend geschlossen.
Bei vollständig fehlendem Text liefert die API eine Fehlermeldung mit OCR-Hinweis.
Bei einzelnen leeren Seiten zeigt sie eine Warnung. Das ist ein Hinweis auf möglicherweise
gescannte Seiten, keine sichere Scan-Erkennung. Gemischte Bild-/Textseiten werden nicht per OCR ergänzt.
Das 10-MiB-Limit prüft die Anwendungslogik nach dem Multipart-Empfang;
ein Upload-Limit vor dem Empfang gehört zu einem späteren Deployment.

### Selbst ausprobieren

1. Lade ein kleines PDF mit auswählbarem Text hoch und vergleiche die Vorschau mit dem Original.
2. Prüfe im Browser unter Netzwerk die POST-Anfrage und ihre JSON-Antwort.
3. Lade ein gescanntes oder leeres PDF hoch und beobachte den OCR-Hinweis.
4. Öffne `/docs` und teste `POST /api/documents/extract` direkt ohne React.

Beispiel einer erfolgreichen Antwort:

```json
{
  "filename": "beispiel.pdf",
  "page_count": 1,
  "pages": [{"page_number": 1, "text": "Text der ersten Seite"}],
  "warnings": []
}
```

## Dokumentation

- Vite: https://vite.dev/guide/
- Tailwind mit Vite: https://tailwindcss.com/docs/installation/using-vite
- FastAPI: https://fastapi.tiangolo.com/tutorial/first-steps/
- Datei-Uploads: https://fastapi.tiangolo.com/tutorial/request-files/
- PyMuPDF-Textextraktion: https://pymupdf.readthedocs.io/en/latest/recipes-text.html

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
