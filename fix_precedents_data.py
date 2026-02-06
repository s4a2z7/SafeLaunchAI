"""
판례 데이터 수정 스크립트
text 필드가 CSS/JS 코드로 되어 있는 문제를 해결
case_name을 text로 사용하도록 수정
"""

import json
import os

def fix_precedents_data():
    """판례 데이터의 text 필드를 case_name으로 교체"""
    
    db_path = "./startup-legal-helper-main/database/precedents.json"
    
    if not os.path.exists(db_path):
        print(f"❌ 파일을 찾을 수 없습니다: {db_path}")
        return
    
    # 데이터 로드
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"📊 총 {len(data)}건의 판례 데이터 발견")
    
    # 수정
    fixed_count = 0
    for doc_id, doc_data in data.items():
        metadata = doc_data.get("metadata", {})
        case_name = metadata.get("case_name", "")
        court_name = metadata.get("court_name", "")
        judgment_date = metadata.get("judgment_date", "")
        
        # 새로운 텍스트 생성 (사건명 + 법원 + 선고일)
        new_text = f"{case_name} {court_name} {judgment_date}"
        
        # text 필드 교체
        doc_data["text"] = new_text
        fixed_count += 1
    
    # 저장
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {fixed_count}건의 판례 데이터 수정 완료!")
    print(f"💾 저장 완료: {db_path}")
    
    # 샘플 출력
    print("\n📝 수정된 데이터 샘플:")
    for i, (doc_id, doc_data) in enumerate(list(data.items())[:3]):
        print(f"\n{i+1}. {doc_data['text'][:100]}...")

if __name__ == "__main__":
    fix_precedents_data()
