"""
기존 precedents.json 오염 데이터 정화 스크립트

Red Team #1 대응: CSS/JS 노이즈로 오염된 판례 데이터를 검증하여
유효하지 않은 청크를 제거합니다.

사용법:
    python clean_precedents.py              # 검증만 (dry-run)
    python clean_precedents.py --apply      # 실제 정화 적용
"""

import json
import os
import sys
import re
from datetime import datetime

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.legal_rag import (
    validate_legal_document,
    _is_noise_text,
    DATABASE_PATH,
    COLLECTION_PRECEDENTS,
)


def clean_precedents(apply: bool = False) -> dict:
    """
    precedents.json에서 노이즈 데이터를 제거

    Args:
        apply: True면 실제로 파일을 수정, False면 검증만 수행

    Returns:
        정화 결과 요약
    """
    file_path = os.path.join(DATABASE_PATH, f"{COLLECTION_PRECEDENTS}.json")

    if not os.path.exists(file_path):
        print(f"[!] 파일이 존재하지 않습니다: {file_path}")
        return {"status": "file_not_found"}

    with open(file_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    total = len(docs)
    valid_docs = {}
    removed_docs = {}

    for doc_id, doc in docs.items():
        text = doc.get("text", "")
        source_type = doc.get("metadata", {}).get("source_type", "precedent")

        is_valid = True

        # 1. 노이즈 패턴 검사
        if _is_noise_text(text):
            is_valid = False

        # 2. 법률 문서 유효성 검증
        if is_valid and not validate_legal_document(text, source_type):
            is_valid = False

        if is_valid:
            valid_docs[doc_id] = doc
        else:
            removed_docs[doc_id] = {
                "case_name": doc.get("metadata", {}).get("case_name", "?"),
                "text_preview": text[:100] if text else "(empty)",
            }

    removed_count = len(removed_docs)
    valid_count = len(valid_docs)

    print(f"\n{'='*60}")
    print(f"판례 데이터 정화 결과")
    print(f"{'='*60}")
    print(f"  전체 문서: {total}건")
    print(f"  유효 문서: {valid_count}건")
    print(f"  제거 대상: {removed_count}건")
    print(f"{'='*60}")

    if removed_docs:
        print(f"\n제거 대상 문서:")
        for doc_id, info in list(removed_docs.items())[:20]:
            print(f"  - [{info['case_name']}] {info['text_preview'][:60]}...")
        if len(removed_docs) > 20:
            print(f"  ... 외 {len(removed_docs) - 20}건")

    if apply:
        # 백업 생성
        backup_path = file_path.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        print(f"\n[*] 백업 저장: {backup_path}")

        # 정화된 데이터 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(valid_docs, f, ensure_ascii=False, indent=2)
        print(f"[*] 정화 완료: {file_path} ({valid_count}건 유지)")
    else:
        print(f"\n[!] dry-run 모드: 실제 변경 없음")
        print(f"    실제 적용하려면: python clean_precedents.py --apply")

    return {
        "total": total,
        "valid": valid_count,
        "removed": removed_count,
        "applied": apply,
    }


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    clean_precedents(apply=apply)
