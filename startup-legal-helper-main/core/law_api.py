"""
국가법령정보 Open API 연동 모듈
https://open.law.go.kr/LSO/openApi/guideList.do

SafeLaunch AI 프로젝트용 Python 버전
"""

import requests
import xmltodict
import json
from typing import Optional, Literal
from dataclasses import dataclass, field

LAW_API_BASE_URL = "https://www.law.go.kr"


@dataclass
class LawApiParams:
    """
    법제처 API 요청 파라미터 클래스
    필수: OC, target, type
    선택: query, display, page, sort 등
    """
    target: str  # API 종류 (law, prec, ordin, lsStmd 등)
    OC: str = "tlduf1"  # 사용자 이메일 ID (@ 앞부분만)
    type: Literal["XML", "JSON", "HTML"] = "XML"
    extra_params: dict = field(default_factory=dict)

    def add_field(self, key: str, value) -> "LawApiParams":
        """추가 파라미터 설정"""
        self.extra_params[key] = value
        return self

    def to_dict(self) -> dict:
        """요청용 딕셔너리 변환"""
        params = {
            "OC": self.OC,
            "target": self.target,
            "type": self.type,
        }
        params.update(self.extra_params)
        return params


def law_api_call(url_path: str, params: LawApiParams, timeout: int = 30) -> dict:
    """
    법제처 API 요청

    Args:
        url_path: API URL 경로 (예: "/DRF/lawSearch.do")
        params: LawApiParams 객체
        timeout: 요청 타임아웃(초)

    Returns:
        dict: 파싱된 응답 (XML→dict 또는 JSON→dict)
    """
    url = LAW_API_BASE_URL + url_path
    try:
        response = requests.get(url, params=params.to_dict(), timeout=timeout)
        response.raise_for_status()

        if params.type == "XML":
            return xmltodict.parse(response.content)
        elif params.type == "JSON":
            return response.json()
        else:
            return {"html": response.text}

    except requests.exceptions.RequestException as e:
        print(f"[LawAPI Error] {e}")
        raise


# ─────────────────────────────────────────────────────────────
# 주요 API 래퍼 함수들
# ─────────────────────────────────────────────────────────────

def search_laws(query: str, display: int = 20, page: int = 1) -> dict:
    """
    법령 검색 (현행법령)
    target: law
    """
    params = LawApiParams(target="law")
    params.add_field("query", query)
    params.add_field("display", display)
    params.add_field("page", page)
    return law_api_call("/DRF/lawSearch.do", params)


def search_precedents(query: str, display: int = 20, page: int = 1) -> dict:
    """
    판례 검색
    target: prec
    """
    params = LawApiParams(target="prec")
    params.add_field("query", query)
    params.add_field("display", display)
    params.add_field("page", page)
    return law_api_call("/DRF/lawSearch.do", params)


def get_law_detail(law_id: str) -> dict:
    """
    법령 본문 조회
    target: law, MST 파라미터로 법령 ID 지정
    """
    params = LawApiParams(target="law")
    params.add_field("MST", law_id)
    return law_api_call("/DRF/lawService.do", params)


def get_precedent_detail(prec_seq: str) -> dict:
    """
    판례 본문 조회
    target: prec, precSeq 파라미터로 판례 일련번호 지정
    """
    params = LawApiParams(target="prec")
    params.add_field("precSeq", prec_seq)
    return law_api_call("/DRF/lawService.do", params)


# ─────────────────────────────────────────────────────────────
# 테스트 실행
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("국가법령정보 Open API 연결 테스트")
    print("=" * 60)

    # 1. 법령 검색 테스트 (예: "저작권")
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

    # 2. 판례 검색 테스트
    print("\n[2] 판례 검색: '저작권 침해'")
    try:
        result = search_precedents("저작권 침해", display=3)
        total = result.get("PrecSearch", {}).get("totalCnt", "N/A")
        print(f"    총 검색 결과: {total}건")

        precs = result.get("PrecSearch", {}).get("prec", [])
        if not isinstance(precs, list):
            precs = [precs] if precs else []

        for i, prec in enumerate(precs[:3], 1):
            name = prec.get("사건명", "N/A")
            seq = prec.get("판례일련번호", "N/A")
            print(f"    {i}. {name} (ID: {seq})")
    except Exception as e:
        print(f"    [실패] {e}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
