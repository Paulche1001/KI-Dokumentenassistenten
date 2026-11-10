import pymupdf

from app.schemas.documents import DocumentExtraction, DocumentPage

MAX_PAGES = 200


class PDFExtractionError(ValueError):
    """Eine Datei kann nicht als unterstütztes Text-PDF verarbeitet werden."""


def extract_pdf(content: bytes, filename: str) -> DocumentExtraction:
    """Liest Text pro Seite und erhält auch die Position leerer Seiten."""
    try:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            if not document.is_pdf:
                raise PDFExtractionError("Die Datei ist kein gültiges PDF.")
            if document.needs_pass:
                raise PDFExtractionError(
                    "Das PDF ist passwortgeschützt. Bitte lade eine ungeschützte Kopie hoch."
                )
            if document.page_count > MAX_PAGES:
                raise PDFExtractionError(f"Bitte verwende ein PDF mit höchstens {MAX_PAGES} Seiten.")

            pages = [
                DocumentPage(page_number=index + 1, text=page.get_text("text", sort=True).strip())
                for index, page in enumerate(document)
            ]
    except (pymupdf.FileDataError, pymupdf.EmptyFileError, RuntimeError) as error:
        raise PDFExtractionError("Das PDF ist beschädigt oder kann nicht gelesen werden.") from error

    if not any(page.text for page in pages):
        raise PDFExtractionError(
            "Das PDF enthält keinen auslesbaren Text. Es könnte ein Scan sein; "
            "eine OCR-Texterkennung ist noch nicht eingebaut."
        )

    empty_pages = [str(page.page_number) for page in pages if not page.text]
    warnings = []
    if empty_pages:
        warnings.append(
            "Kein auslesbarer Text auf Seite(n): " + ", ".join(empty_pages)
            + ". Diese Seiten sind leer oder benötigen möglicherweise OCR."
        )

    return DocumentExtraction(
        filename=filename, page_count=len(pages), pages=pages, warnings=warnings
    )
