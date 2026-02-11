from pydantic import BaseModel


class DocumentInput(BaseModel):
    content: str
    metadata: dict | None = None


class BatchDocumentInput(BaseModel):
    documents: list[DocumentInput]


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    content: str
    metadata: dict
    distance: float | None = None


class RagStats(BaseModel):
    voc_count: int
    guide_count: int
