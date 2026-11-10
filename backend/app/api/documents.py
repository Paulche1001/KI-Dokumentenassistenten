from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas.documents import DocumentExtraction
from app.services.pdf import PDFExtractionError, extract_pdf

router = APIRouter(prefix="/api/documents", tags=["documents"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/extract", response_model=DocumentExtraction)
def extract_document(file: UploadFile) -> DocumentExtraction:
    """Nimmt ein PDF entgegen und gibt Text zurück, ohne es dauerhaft zu speichern."""
    try:
        filename = file.filename or ""
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=415, detail="Bitte lade eine PDF-Datei (.pdf) hoch.")

        # Ein Byte mehr lesen, damit wir eine Überschreitung erkennen.
        content = file.file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Das PDF darf höchstens 10 MiB groß sein.")
        if not content:
            raise HTTPException(status_code=422, detail="Die hochgeladene Datei ist leer.")

        try:
            return extract_pdf(content, filename)
        except PDFExtractionError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
    finally:
        file.file.close()
