from app.schemas.chunks import DocumentChunk
from app.schemas.documents import DocumentPage

def split_text(text: str, chunk_size: int, overlap: int = 0) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("Die Chunk-Größe muss größer als 0 sein.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Die Überlappung muss zwischen 0 und der Chunk-Größe liegen.")

    chunks = []

    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start + overlap:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
        
    return chunks

def chunk_pages(
    pages: list[DocumentPage],
    chunk_size: int,
    overlap: int = 0,
) -> list[DocumentChunk]:
    """Teilt Dokumentseiten anhand von Chunk-Größe und Überlappung auf.

    Gibt DocumentChunk-Objekte mit fortlaufenden Indizes und ursprünglichen
    Seitennummern zurück. Seiten ohne Text erzeugen keine Chunks.
    """
    chunks = []
    for page in pages:
        page_chunks = split_text(page.text, chunk_size, overlap)
        for chunk in page_chunks:
            document_chunk = DocumentChunk(
                chunk_index=len(chunks),
                page_number=page.page_number,
                text=chunk,
            )
            chunks.append(document_chunk)
    return chunks

if __name__ == "__main__":
    pages = [
        DocumentPage(page_number=1, text="Eins zwei drei"),
        DocumentPage(page_number=2, text=""),
        DocumentPage(page_number=3, text="Vier fünf sechs"),
    ]

    for chunk in chunk_pages(pages, 10, 0):
        print(chunk)

