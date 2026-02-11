from fastapi import APIRouter, UploadFile, File

from app.dependencies import get_rag_service
from app.schemas.rag import (
    BatchDocumentInput,
    DocumentInput,
    RagStats,
    SearchRequest,
    SearchResult,
)

router = APIRouter(prefix="/api/rag", tags=["rag"])


# ── 통계 ──

@router.get("/stats", response_model=RagStats)
async def get_stats():
    rag = get_rag_service()
    return RagStats(
        voc_count=rag.get_voc_count(),
        guide_count=rag.get_guide_count(),
    )


# ── VOC 데이터 ──

@router.post("/vocs", summary="VOC 1건 추가")
async def add_voc(doc: DocumentInput):
    rag = get_rag_service()
    doc_id = rag.add_voc(doc.content, doc.metadata)
    return {"id": doc_id}


@router.post("/vocs/batch", summary="VOC 여러건 일괄 추가")
async def add_vocs_batch(batch: BatchDocumentInput):
    rag = get_rag_service()
    contents = [d.content for d in batch.documents]
    metadatas = [d.metadata or {} for d in batch.documents]
    ids = rag.add_vocs_batch(contents, metadatas)
    return {"count": len(ids), "ids": ids}


@router.post("/vocs/upload", summary="VOC 텍스트 파일 업로드 (줄 단위 분리)")
async def upload_vocs_file(file: UploadFile = File(...)):
    rag = get_rag_service()
    raw = await file.read()
    text = raw.decode("utf-8")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    metadatas = [{"source": file.filename}] * len(lines)
    ids = rag.add_vocs_batch(lines, metadatas)
    return {"count": len(ids), "filename": file.filename}


@router.post("/vocs/search", response_model=list[SearchResult])
async def search_vocs(req: SearchRequest):
    rag = get_rag_service()
    results = rag.search_vocs(req.query, top_k=req.top_k)
    return results


# ── 가이드 문서 ──

@router.post("/guides", summary="가이드 1건 추가")
async def add_guide(doc: DocumentInput):
    rag = get_rag_service()
    doc_id = rag.add_guide(doc.content, doc.metadata)
    return {"id": doc_id}


@router.post("/guides/batch", summary="가이드 여러건 일괄 추가")
async def add_guides_batch(batch: BatchDocumentInput):
    rag = get_rag_service()
    contents = [d.content for d in batch.documents]
    metadatas = [d.metadata or {} for d in batch.documents]
    ids = rag.add_guides_batch(contents, metadatas)
    return {"count": len(ids), "ids": ids}


@router.post("/guides/upload", summary="가이드 텍스트 파일 업로드 (빈 줄 기준 단락 분리)")
async def upload_guides_file(file: UploadFile = File(...)):
    rag = get_rag_service()
    raw = await file.read()
    text = raw.decode("utf-8")
    # 빈 줄 기준으로 단락 분리
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    metadatas = [{"source": file.filename, "title": file.filename}] * len(paragraphs)
    ids = rag.add_guides_batch(paragraphs, metadatas)
    return {"count": len(ids), "filename": file.filename}


@router.post("/guides/search", response_model=list[SearchResult])
async def search_guides(req: SearchRequest):
    rag = get_rag_service()
    results = rag.search_guides(req.query, top_k=req.top_k)
    return results
