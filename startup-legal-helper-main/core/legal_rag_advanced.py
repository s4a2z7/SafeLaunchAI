"""
SafeLaunch AI - Advanced Legal RAG Engine (Numpy Implementation)
startup-legal-helper-main/core/legal_rag_advanced.py

ChromaDB의 Python 3.14 호환성 이슈로 인해, 
Numpy와 Sentence-Transformers를 사용하는 경량화된 
벡터 검색 엔진으로 대체 구현되었습니다.
"""

import os
import json
import numpy as np
import pathlib
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────────────────────
# 설정 및 경로
# ─────────────────────────────────────────────────────────────

from core.legal_rag import DATABASE_PATH, ALL_COLLECTIONS

_CURRENT_DIR = pathlib.Path(__file__).parent.parent.parent
VECTOR_DB_PATH = str(_CURRENT_DIR / "startup-legal-helper-db" / "vector_cache")
MODEL_NAME = "jhgan/ko-sroberta-multitask"

class NumpyVectorStore:
    """
    Numpy 기반 경량 벡터 스토어
    """
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.cache_dir = os.path.join(VECTOR_DB_PATH, collection_name)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.embeddings_file = os.path.join(self.cache_dir, "embeddings.npy")
        self.metadata_file = os.path.join(self.cache_dir, "metadata.json")
        
        self.embeddings: Optional[np.ndarray] = None
        self.metadata: List[Dict] = []
        self.documents: List[str] = []
        
        self._load()

    def _load(self):
        if os.path.exists(self.embeddings_file) and os.path.exists(self.metadata_file):
            self.embeddings = np.load(self.embeddings_file)
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.metadata = data["metadatas"]
                self.documents = data["documents"]

    def _save(self):
        if self.embeddings is not None:
            np.save(self.embeddings_file, self.embeddings)
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump({"metadatas": self.metadata, "documents": self.documents}, f, ensure_ascii=False, indent=2)

    def upsert(self, embeddings: np.ndarray, documents: List[str], metadatas: List[Dict]):
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
        
        self.documents.extend(documents)
        self.metadata.extend(metadatas)
        self._save()

    def query(self, query_embedding: np.ndarray, n_results: int = 5) -> List[Dict]:
        if self.embeddings is None or len(self.embeddings) == 0:
            return []

        # Cosine Similarity: (A · B) / (||A|| * ||B||)
        # 이미 정규화되어 있다고 가정하거나 여기서 계산
        norm_query = query_embedding / np.linalg.norm(query_embedding)
        norm_embeddings = self.embeddings / np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        
        similarities = np.dot(norm_embeddings, norm_query)
        
        # 상위 N개 인덱스
        top_indices = np.argsort(similarities)[::-1][:n_results]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(similarities[idx])
            })
        return results

class AdvancedLegalRAG:
    def __init__(self):
        print(f"[AdvancedRAG] 모델 로딩 중: {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.stores = {name: NumpyVectorStore(name) for name in ALL_COLLECTIONS}
        print("[AdvancedRAG] 시스템 준비 완료.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.model.encode([query])[0]
        
        all_hits = []
        for name, store in self.stores.items():
            hits = store.query(query_embedding, n_results=top_k)
            all_hits.extend(hits)
        
        all_hits.sort(key=lambda x: x["score"], reverse=True)
        return all_hits[:top_k]

# 싱글톤
_rag = None
def get_advanced_rag():
    global _rag
    if _rag is None:
        _rag = AdvancedLegalRAG()
    return _rag

def search_legal_context(query: str, top_k: int = 5, score_threshold: float = 0.3) -> List[Dict]:
    try:
        rag = get_advanced_rag()
        results = rag.search(query, top_k=top_k)
        filtered = [r for r in results if r["score"] >= score_threshold]
        
        # Fallback 전략: 결과가 없으면 임계치를 낮춰서 다시 시도
        if not filtered and results:
            print("[AdvancedRAG] Fallback: 검색 결과가 없어 임계치를 0.1로 낮춥니다.")
            filtered = [r for r in results if r["score"] >= 0.1]
            
        return filtered
    except Exception as e:
        print(f"[AdvancedRAG] 검색 에러: {e}")
        return []

# ─────────────────────────────────────────────────────────────
# 동기화 및 마이그레이션
# ─────────────────────────────────────────────────────────────

def migrate_json_to_numpy():
    rag = get_advanced_rag()
    for col in ALL_COLLECTIONS:
        json_path = os.path.join(DATABASE_PATH, f"{col}.json")
        if not os.path.exists(json_path): continue
        
        print(f"[AdvancedRAG] 마이그레이션 중: {col}...")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            texts = [v["text"] for v in data.values()]
            metas = [v["metadata"] for v in data.values()]
            
            if texts:
                embeddings = rag.model.encode(texts, batch_size=32, show_progress_bar=True)
                rag.stores[col].upsert(embeddings, texts, metas)
        print(f"[AdvancedRAG] {col} 완료.")

if __name__ == "__main__":
    migrate_json_to_numpy()
    # 테스트 검색
    print(search_legal_context("저작권 침해", top_k=2))
