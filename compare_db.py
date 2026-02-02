import json

# 두 데이터베이스 비교
db1_path = r"c:\Users\LG\Desktop\정부지원과제및리스크분석\startup-legal-helper-main\database"
db2_path = r"c:\Users\LG\Desktop\정부지원과제및리스크분석\startup-legal-helper-db\startup-legal-helper-db_deisgner\database"

print("=" * 60)
print("📊 데이터베이스 비교")
print("=" * 60)

for filename in ["laws.json", "precedents.json", "store_policies.json"]:
    print(f"\n📁 {filename}")
    print("-" * 60)
    
    # DB1
    with open(f"{db1_path}/{filename}", "r", encoding="utf-8") as f:
        data1 = json.load(f)
        print(f"  DB1 (startup-legal-helper-main): {len(data1):,}개")
    
    # DB2
    with open(f"{db2_path}/{filename}", "r", encoding="utf-8") as f:
        data2 = json.load(f)
        print(f"  DB2 (startup-legal-helper-db):   {len(data2):,}개")
    
    # 차이
    diff = len(data1) - len(data2)
    if diff > 0:
        print(f"  ⚠️  DB1이 {diff:,}개 더 많음")
    elif diff < 0:
        print(f"  ⚠️  DB2가 {abs(diff):,}개 더 많음")
    else:
        print(f"  ✅ 동일")

print("\n" + "=" * 60)
print("💡 권장사항")
print("=" * 60)

# 파일 크기 비교
import os
print(f"\nDB1 laws.json 크기: {os.path.getsize(f'{db1_path}/laws.json'):,} bytes")
print(f"DB2 laws.json 크기: {os.path.getsize(f'{db2_path}/laws.json'):,} bytes")
