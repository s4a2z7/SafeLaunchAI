"""
판례 재수집 스크립트

개선된 추출 로직(노이즈 필터링 + 품질 검증)으로 판례를 재수집합니다.
기존 0131vectordbprompt.md의 수집 키워드를 동일하게 사용합니다.

사용법:
    python reingest_precedents.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.legal_rag import (
    ingest_precedents,
    get_or_create_collection,
    COLLECTION_PRECEDENTS,
)

# 기존 수집에 사용된 키워드 (0131vectordbprompt.md 기준)
PRECEDENT_QUERIES = [
    "저작권 침해",
    "프로그램 저작권",
    "영업비밀 침해",
    "개인정보 유출",
    "개인정보 처리",
    "소비자 보호",
    "온라인 서비스",
    "디지털 콘텐츠",
    "정보통신망 침해",
    "특허 침해",
    "상표권 침해",
    "부정경쟁 모방",
    "콘텐츠 저작권",
]


def main():
    print("=" * 60)
    print("판례 재수집 시작 (개선된 추출 로직 적용)")
    print("=" * 60)

    store = get_or_create_collection(COLLECTION_PRECEDENTS)
    print(f"현재 precedents 컬렉션: {store.count()}건\n")

    total_chunks = 0

    for i, query in enumerate(PRECEDENT_QUERIES, 1):
        print(f"\n[{i}/{len(PRECEDENT_QUERIES)}] 키워드: '{query}'")
        print("-" * 40)
        chunks = ingest_precedents(query, max_items=10)
        total_chunks += chunks
        print(f"  → {chunks}청크 적재")

    # 최종 결과
    store_final = get_or_create_collection(COLLECTION_PRECEDENTS)
    # 캐시 갱신을 위해 reload
    store_final._load()
    final_count = store_final.count()

    print(f"\n{'=' * 60}")
    print(f"판례 재수집 완료")
    print(f"  이번 실행 적재: {total_chunks}청크")
    print(f"  컬렉션 최종: {final_count}건")
    print(f"{'=' * 60}")

    # 품질 확인: 샘플 텍스트 출력
    if final_count > 0:
        print(f"\n샘플 데이터 확인 (상위 5건):")
        print("-" * 60)
        count = 0
        for doc_id, doc in list(store_final._docs.items())[:5]:
            meta = doc["metadata"]
            text_preview = doc["text"][:120].replace("\n", " ")
            print(f"  [{meta.get('case_name', '?')}]")
            print(f"    법원: {meta.get('court_name', '?')} | 날짜: {meta.get('judgment_date', '?')}")
            print(f"    텍스트: {text_preview}...")
            print()
            count += 1


if __name__ == "__main__":
    main()
