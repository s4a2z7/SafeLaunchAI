"""
SafeLaunch AI - Solution Engine
startup-legal-helper-main/core/solution_engine.py

이 모듈은 RAG를 통해 발견된 법률 리스크 포인트에 대해 
기술적/구조적 우회 전략(Bypass Strategy) 및 대안 솔루션을 제안합니다.
"""

from typing import List, Dict

class SolutionEngine:
    """
    리스크 유형별 솔루션 매핑 및 대안 생성 엔진
    """
    
    # 리스크 키워드별 표준 솔루션 맵
    STRATEGY_MAP = {
        "저작권": {
            "patterns": ["무단 수집", "복제", "2차 저작물", "크롤링"],
            "solutions": [
                "1. 공정 이용(Fair Use) 가이드라인 준수: 영리적 목적 외에 교육/연구/비평 목적으로 변형적 활용(Transformative Use) 강조.",
                "2. 데이터 원천 차별화: 자체 생성 데이터(LLM Synthetic Data) 비율 확대 및 출처 명기(Attribution) 강화.",
                "3. API 약관 우회: 재배포 금지 시, 원본 데이터가 아닌 '가공된 통계/추상화된 데이터'만 노출하도록 아키텍처 변경."
            ]
        },
        "개인정보": {
            "patterns": ["제3자 제공", "수집 동의", "위치정보", "민감데이터"],
            "solutions": [
                "1. 로컬 처리 전환: 서버 수집 없이 사용자 기기 내(Edger AI/Local Storage)에서만 처리하도록 변경.",
                "2. 익명화/가명화 강화: 개인 식별 정보(PII)를 비가역적으로 암호화하거나 합성 데이터로 대체.",
                "3. 동의 UI 고도화: '포괄적 동의'가 아닌 '기능별 선택 동의'로 UI/UX 세분화하여 리젝 위험 방해."
            ]
        },
        "특허": {
            "patterns": ["기능 유사", "UI 카피", "동일 로직"],
            "solutions": [
                "1. 기술적 우회 설계(Design Around): 핵심 구성 요소 중 하나를 완전히 다른 메커니즘으로 교체하여 특허의 '모든 구성 요소 불침해' 원칙 적용.",
                "2. 선행기술 조사 기반 차별화: 기존 특허의 공백 영역을 찾아내어 해당 영역으로 서비스 로직 집중.",
                "3. 오픈소스 대안: 특허가 걸린 상용 라이브러리 대신, 권리 관계가 깨끗한 Permissive License(MIT/Apache) 기반으로 재구현."
            ]
        }
    }

    def suggest_solutions(self, analysis_results: List[Dict]) -> List[str]:
        """
        분석 결과(RAG 결과물)에서 리스크 패턴을 분석하여 솔루션 제안
        """
        suggested = []
        found_categories = set()

        for result in analysis_results:
            text = result.get("text", "")
            for category, data in self.STRATEGY_MAP.items():
                if any(p in text for p in data["patterns"]):
                    if category not in found_categories:
                        suggested.extend(data["solutions"])
                        found_categories.add(category)

        # 기본 일반 솔루션
        if not suggested:
            suggested.append("범용 솔루션: 서비스 설명의 독창성(Originality)을 강화하고, 서비스 이용 약관에 법적 면책 조항을 명확히 명시하십시오.")

        return suggested

if __name__ == "__main__":
    # 간단한 테스트
    engine = SolutionEngine()
    test_results = [{"text": "저작권법 제103조에 따른 무단 수집 리스크가 발견되었습니다."}]
    solutions = engine.suggest_solutions(test_results)
    for s in solutions:
        print(s)
