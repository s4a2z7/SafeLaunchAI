import json
import sys

db_path = r"c:\Users\LG\Desktop\정부지원과제및리스크분석\startup-legal-helper-db\startup-legal-helper-db_deisgner\database"

# 법률 조항 확인
with open(f"{db_path}/laws.json", "r", encoding="utf-8") as f:
    laws = json.load(f)
    print(f"✅ 법률 조항 수: {len(laws):,}개")
    print(f"   데이터 타입: {type(laws)}")
    if isinstance(laws, dict):
        first_key = list(laws.keys())[0] if laws else None
        if first_key:
            print(f"   첫 번째 항목 키: {list(laws[first_key].keys())}")
    elif isinstance(laws, list) and laws:
        print(f"   첫 번째 항목 키: {list(laws[0].keys())}")

# 판례 확인
with open(f"{db_path}/precedents.json", "r", encoding="utf-8") as f:
    precedents = json.load(f)
    print(f"\n✅ 판례 수: {len(precedents):,}건")
    print(f"   데이터 타입: {type(precedents)}")

# 스토어 정책 확인
with open(f"{db_path}/store_policies.json", "r", encoding="utf-8") as f:
    policies = json.load(f)
    print(f"\n✅ 스토어 정책 수: {len(policies):,}개")
    print(f"   데이터 타입: {type(policies)}")

