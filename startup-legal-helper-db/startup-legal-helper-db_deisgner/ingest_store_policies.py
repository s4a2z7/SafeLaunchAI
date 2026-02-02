"""
스토어 정책 데이터 적재 스크립트
ingest_store_policies.py

사용법:
    python ingest_store_policies.py              # 기존 데이터에 추가
    python ingest_store_policies.py --refresh    # 기존 데이터 삭제 후 재적재
"""

import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.legal_rag import ingest_store_policies, get_or_create_collection, COLLECTION_POLICIES
from core.store_policy_data import get_all_store_policies


def main():
    force_refresh = "--refresh" in sys.argv

    print("=" * 60)
    print("SafeLaunch AI — 스토어 정책 데이터 적재")
    print("=" * 60)

    # 적재 전 상태
    store = get_or_create_collection(COLLECTION_POLICIES)
    print(f"\n[적재 전] store_policies: {store.count()}건")

    # 정책 데이터 로드
    policies = get_all_store_policies()
    apple_count = sum(1 for p in policies if p["metadata"]["store"] == "apple")
    google_count = sum(1 for p in policies if p["metadata"]["store"] == "google")
    print(f"\n[원본 데이터] Apple: {apple_count}건, Google: {google_count}건")

    if force_refresh:
        print("\n⚠ --refresh 옵션: 기존 데이터 삭제 후 재적재")

    # 적재 실행
    print("\n" + "-" * 40)
    total_chunks = ingest_store_policies(policies, force_refresh=force_refresh)
    print("-" * 40)

    # 적재 후 상태
    # 캐시 초기화를 위해 새로 로드
    store = get_or_create_collection(COLLECTION_POLICIES)
    print(f"\n[적재 후] store_policies: {store.count()}건 (신규 청크: {total_chunks})")

    # 검색 테스트
    print("\n" + "=" * 60)
    print("검색 테스트")
    print("=" * 60)

    test_queries = [
        "앱 내 결제 인앱 구매 정책",
        "개인정보 수집 동의 프라이버시",
        "앱 카피 사칭 지적재산권 침해",
        "어린이 아동 보호 키즈 카테고리",
        "앱 스토어 메타데이터 스크린샷 설명",
        "구독 자동 갱신 환불",
        "광고 정책 전면 광고",
        "UGC 사용자 생성 콘텐츠 필터링",
    ]

    for query in test_queries:
        results = store.query(query_text=query, n_results=3)
        if results:
            top = results[0]
            score = top["score"]
            store_name = top["metadata"].get("store", "?")
            section = top["metadata"].get("section", "?")
            subsection = top["metadata"].get("subsection", "?")
            print(f"\n  Q: {query}")
            print(f"  → [{score:.3f}] [{store_name}] {section} > {subsection}")
            print(f"    {top['text'][:100]}...")
        else:
            print(f"\n  Q: {query}")
            print(f"  → 결과 없음")

    print("\n" + "=" * 60)
    print("적재 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
