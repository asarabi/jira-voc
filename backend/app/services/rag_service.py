import logging
import uuid
from pathlib import Path

import chromadb

logger = logging.getLogger(__name__)

# 컬렉션 이름
COLLECTION_VOCS = "past_vocs"
COLLECTION_GUIDES = "guides"


class RagService:
    def __init__(self, persist_dir: str | None = None):
        if persist_dir is None:
            persist_dir = str(
                Path(__file__).parent.parent.parent / "chromadb_data"
            )
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._vocs = self._client.get_or_create_collection(
            name=COLLECTION_VOCS,
            metadata={"description": "과거 VOC 데이터"},
        )
        self._guides = self._client.get_or_create_collection(
            name=COLLECTION_GUIDES,
            metadata={"description": "가이드 문서"},
        )
        logger.info(
            "RAG initialized: vocs=%d, guides=%d",
            self._vocs.count(),
            self._guides.count(),
        )

    # ── VOC 관리 ──

    def add_voc(
        self,
        content: str,
        metadata: dict | None = None,
        doc_id: str | None = None,
    ) -> str:
        doc_id = doc_id or str(uuid.uuid4())
        self._vocs.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )
        return doc_id

    def add_vocs_batch(
        self,
        contents: list[str],
        metadatas: list[dict] | None = None,
    ) -> list[str]:
        ids = [str(uuid.uuid4()) for _ in contents]
        if metadatas is None:
            metadatas = [{} for _ in contents]
        self._vocs.add(documents=contents, metadatas=metadatas, ids=ids)
        return ids

    def search_vocs(self, query: str, top_k: int = 5) -> list[dict]:
        results = self._vocs.query(query_texts=[query], n_results=top_k)
        return self._format_results(results)

    def get_voc_count(self) -> int:
        return self._vocs.count()

    # ── 가이드 관리 ──

    def add_guide(
        self,
        content: str,
        metadata: dict | None = None,
        doc_id: str | None = None,
    ) -> str:
        doc_id = doc_id or str(uuid.uuid4())
        self._guides.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )
        return doc_id

    def add_guides_batch(
        self,
        contents: list[str],
        metadatas: list[dict] | None = None,
    ) -> list[str]:
        ids = [str(uuid.uuid4()) for _ in contents]
        if metadatas is None:
            metadatas = [{} for _ in contents]
        self._guides.add(documents=contents, metadatas=metadatas, ids=ids)
        return ids

    def search_guides(self, query: str, top_k: int = 5) -> list[dict]:
        results = self._guides.query(query_texts=[query], n_results=top_k)
        return self._format_results(results)

    def get_guide_count(self) -> int:
        return self._guides.count()

    # ── 통합 검색 (VOC + 가이드 동시) ──

    def search_all(self, query: str, top_k: int = 3) -> dict:
        vocs = self.search_vocs(query, top_k=top_k)
        guides = self.search_guides(query, top_k=top_k)
        return {"vocs": vocs, "guides": guides}

    def format_context_for_prompt(self, query: str, top_k: int = 3) -> str:
        """검색 결과를 AI 프롬프트에 넣을 수 있는 텍스트로 변환"""
        results = self.search_all(query, top_k=top_k)
        parts = []

        if results["vocs"]:
            parts.append("=== 유사 과거 VOC 사례 ===")
            for i, doc in enumerate(results["vocs"], 1):
                meta = doc.get("metadata", {})
                source = meta.get("source", "")
                label = f" ({source})" if source else ""
                parts.append(f"[사례 {i}]{label}\n{doc['content']}")

        if results["guides"]:
            parts.append("\n=== 관련 가이드 ===")
            for i, doc in enumerate(results["guides"], 1):
                meta = doc.get("metadata", {})
                title = meta.get("title", f"가이드 {i}")
                parts.append(f"[{title}]\n{doc['content']}")

        return "\n\n".join(parts) if parts else ""

    # ── 내부 유틸 ──

    def _format_results(self, raw: dict) -> list[dict]:
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]
        ids = raw.get("ids", [[]])[0]
        return [
            {
                "id": ids[i],
                "content": docs[i],
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else None,
            }
            for i in range(len(docs))
        ]
