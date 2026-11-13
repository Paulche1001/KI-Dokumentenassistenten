from pydantic import BaseModel

class DocumentChunk(BaseModel):
    chunk_index: int
    page_number: int
    text: str