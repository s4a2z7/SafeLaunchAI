"""
RAG 검색 테스트 스크립트
판례 검색이 제대로 작동하는지 확인
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'startup-legal-helper-main'))

from core.legal_rag import (
    search_legal_context,
    get_or_create_collection,
    ALL_COLLECTIONS
)

def test_search():
    """검색 테스트"""
    
    print("=" * 60)
    print("RAG 검색 테스트")
    print("=" * 60)
    
    # 1. 컬렉션 상태 확인
    print("\n[1] 컬렉션 상태:")
    for col_name in ALL_COLLECTIONS:
        store = get_or_create_collection(col_name)
        count = store.count()
        print(f"  - {col_name}: {count}건")
    
    # 2. 검색 테스트
    test_queries = [
        "저작권 침해",
        "개인정보 유출",
        "뉴스 기사",
        "AI 요약"
    ]
    
    for query in test_queries:
        print(f"\n[검색] '{query}'")
        results = search_legal_context(
            query=query,
            top_k=5,
            score_threshold=0.0  # 모든 결과 표시
        )
        
        print(f"  총 {len(results)}건 발견")
        
        # 결과 분류
        by_type = {"law": 0, "precedent": 0, "policy": 0}
        for r in results:
            source_type = r.get("metadata", {}).get("source_type", "unknown")
            if "law" in source_type:
                by_type["law"] += 1
            elif "precedent" in source_type:
                by_type["precedent"] += 1
            elif "policy" in source_type:
                by_type["policy"] += 1
        
        print(f"  - 법률: {by_type['law']}건")
        print(f"  - 판례: {by_type['precedent']}건")
        print(f"  - 정책: {by_type['policy']}건")
        
        # 상위 3개 결과 출력
        for i, r in enumerate(results[:3], 1):
            score = r.get("score", 0)
            text = r.get("text", "")[:80]
            source_type = r.get("metadata", {}).get("source_type", "?")
            print(f"  {i}. [{score:.3f}] {source_type}: {text}...")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_search()
