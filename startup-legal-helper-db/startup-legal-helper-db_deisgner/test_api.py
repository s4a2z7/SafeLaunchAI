# -*- coding: utf-8 -*-
"""국가법령정보 API 연결 테스트"""

import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

from core.law_api import search_laws, search_precedents

print("=" * 60)
print("국가법령정보 Open API 연결 테스트")
print("=" * 60)

# 1. 법령 검색
print("\n[1] 법령 검색: '저작권'")
try:
    result = search_laws("저작권", display=5)
    total = result.get("LawSearch", {}).get("totalCnt", "N/A")
    print(f"    총 검색 결과: {total}건")

    laws = result.get("LawSearch", {}).get("law", [])
    if not isinstance(laws, list):
        laws = [laws] if laws else []

    for i, law in enumerate(laws[:5], 1):
        name = law.get("법령명한글", "N/A")
        mst = law.get("법령일련번호", "N/A")
        print(f"    {i}. {name} (ID: {mst})")
except Exception as e:
    print(f"    [실패] {e}")

# 2. 판례 검색
print("\n[2] 판례 검색: '저작권 침해'")
try:
    result2 = search_precedents("저작권 침해", display=3)
    total2 = result2.get("PrecSearch", {}).get("totalCnt", "N/A")
    print(f"    총 검색 결과: {total2}건")

    precs = result2.get("PrecSearch", {}).get("prec", [])
    if not isinstance(precs, list):
        precs = [precs] if precs else []

    for i, prec in enumerate(precs[:3], 1):
        name = prec.get("사건명", "N/A")
        seq = prec.get("판례일련번호", "N/A")
        print(f"    {i}. {name} (ID: {seq})")
except Exception as e:
    print(f"    [실패] {e}")

print("\n" + "=" * 60)
print("API 연결 성공!")
print("=" * 60)

# JSON 샘플 저장
with open("api_sample_output.json", "w", encoding="utf-8") as f:
    json.dump({
        "laws_sample": result.get("LawSearch", {}).get("law", [])[:2] if "result" in dir() else [],
        "precs_sample": result2.get("PrecSearch", {}).get("prec", [])[:2] if "result2" in dir() else []
    }, f, ensure_ascii=False, indent=2)
    print("\n샘플 데이터 저장: api_sample_output.json")
