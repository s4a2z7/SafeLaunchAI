"""
LangChain RAG 데이터 적재 스크립트
ingest_langchain.py

사용법:
    python ingest_langchain.py              # 기존 데이터에 추가
    python ingest_langchain.py --refresh    # 기존 데이터 삭제 후 재적재
    python ingest_langchain.py --test       # 적재 후 검색 테스트

필수 환경 변수:
    OPENAI_API_KEY - OpenAI API 키 (.env 파일에 설정)
"""

import sys
import os

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from core.langchain_rag import (
    ingest_all_data,
    search_legal_context,
    search_store_policies,
    get_collection_stats,
)


def main():
    force_refresh = "--refresh" in sys.argv
    run_test = "--test" in sys.argv

    print("=" * 60)
    print("SafeLaunch AI - LangChain RAG 데이터 적재")
    print("=" * 60)

    # API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[ERROR] OPENAI_API_KEY가 설정되지 않았습니다.")
        print("  1. .env.example을 .env로 복사하세요")
        print("  2. .env 파일에 OPENAI_API_KEY를 설정하세요")
        return

    # 적재 전 상태
    print("\n[적재 전] 컬렉션 상태:")
    stats_before = get_collection_stats()
    for name, count in stats_before.items():
        print(f"  {name}: {count}건")

    if force_refresh:
        print("\n--refresh 옵션: 기존 데이터 삭제 후 재적재")

    # 적재 실행
    print("\n" + "-" * 40)
    result = ingest_all_data(force_refresh=force_refresh)
    print("-" * 40)

    # 적재 후 상태
    print("\n[적재 후] 컬렉션 상태:")
    stats_after = get_collection_stats()
    for name, count in stats_after.items():
        print(f"  {name}: {count}건")

    print(f"\n[결과] 총 {result['total']}개 청크 적재")

    # 검색 테스트
    if run_test:
        print("\n" + "=" * 60)
        print("검색 테스트")
        print("=" * 60)

        test_queries = [
            "앱 내 결제 인앱 구매 정책",
            "개인정보 수집 동의 프라이버시",
            "저작권 침해 카피 사칭",
            "어린이 아동 보호 키즈 카테고리",
            "구독 자동 갱신 환불",
        ]

        for query in test_queries:
            results = search_legal_context(query, top_k=2, score_threshold=0.2)
            print(f"\nQ: {query}")

            if results:
                for r in results:
                    score = r["score"]
                    source_type = r["metadata"].get("source_type", "?")
                    store = r["metadata"].get("store", "")
                    section = r["metadata"].get("section", "")
                    print(f"  [{score:.3f}] [{source_type}] {store} {section}")
                    print(f"    {r['text'][:100]}...")
            else:
                print("  결과 없음")

        # Apple vs Google 필터 테스트
        print("\n" + "-" * 40)
        print("스토어 필터 테스트: '인앱 구매'")

        print("\n[Apple만]")
        apple_results = search_store_policies("인앱 구매", top_k=2, store_filter="apple")
        for r in apple_results:
            print(f"  [{r['score']:.3f}] {r['metadata'].get('section', '')}")

        print("\n[Google만]")
        google_results = search_store_policies("인앱 구매", top_k=2, store_filter="google")
        for r in google_results:
            print(f"  [{r['score']:.3f}] {r['metadata'].get('section', '')}")

    print("\n" + "=" * 60)
    print("완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
