from typing import List


class VectorStore:
    """Semantic vector store using ChromaDB with keyword fallback."""

    def __init__(self):
        self._collection = None
        self._documents: List[str] = []
        self._use_chroma = self._try_init_chroma()

    def _try_init_chroma(self) -> bool:
        try:
            import chromadb
            self._chroma_client = chromadb.EphemeralClient()
            self._collection = self._chroma_client.create_collection(
                name="product_strategy_docs",
                metadata={"hnsw:space": "cosine"},
            )
            return True
        except Exception:
            return False

    def add_documents(self, processed_data: dict) -> None:
        docs = processed_data.get("documents", [])
        if not docs:
            return
        self._documents = [d for d in docs if d.strip()]
        if self._use_chroma and self._collection:
            try:
                batch = self._documents[:500]
                self._collection.add(
                    documents=batch,
                    ids=[f"doc_{i}" for i in range(len(batch))],
                )
            except Exception:
                self._use_chroma = False

    def query(self, question: str, n_results: int = 4) -> List[str]:
        if self._use_chroma and self._collection:
            try:
                result = self._collection.query(query_texts=[question], n_results=min(n_results, len(self._documents)))
                return result["documents"][0] if result["documents"] else []
            except Exception:
                pass
        return self._keyword_search(question, n_results)

    def _keyword_search(self, query: str, n: int) -> List[str]:
        query_words = set(query.lower().split())
        scored = []
        for doc in self._documents:
            doc_words = set(doc.lower().split())
            score = len(query_words & doc_words)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:n]]
