"""
스토어 정책 원본 데이터 — Apple App Store / Google Play Store
core/store_policy_data.py

SafeLaunch AI 프로젝트용
- Apple App Store Review Guidelines (2026-01 기준)
- Google Play Developer Program Policy (2026-01 기준)
- ingest_store_policies()로 store_policies 컬렉션에 적재
"""

# ─────────────────────────────────────────────────────────────
# Apple App Store Review Guidelines
# ─────────────────────────────────────────────────────────────

APPLE_POLICIES: list[dict] = [
    # ── 1. Safety ──
    {
        "text": (
            "[Apple App Store 심사 가이드라인 1.1 부적절한 콘텐츠] "
            "앱에는 공격적이거나, 무감각하거나, 불쾌하거나, 혐오감을 주거나, 극히 저속하거나 소름 끼치는 콘텐츠가 포함되어서는 안 됩니다. "
            "1.1.1 종교, 인종, 성적 지향, 성별, 국적/민족적 출신 또는 기타 대상 그룹에 대한 비방적, 차별적 또는 악의적인 콘텐츠. "
            "특히 대상 개인이나 그룹을 모욕하거나 위협하거나 해를 끼칠 가능성이 있는 앱은 거부됩니다. "
            "1.1.2 사실적으로 묘사된 사람이나 동물의 살해, 훼손, 고문 또는 학대, 또는 폭력을 조장하는 콘텐츠. "
            "1.1.3 무기 및 위험 물체의 불법적이거나 무모한 사용을 조장하는 묘사, 또는 총기나 탄약 구매를 용이하게 하는 묘사. "
            "1.1.4 노골적인 성적 또는 음란 자료. 이는 성적 흥분을 유발하기 위한 것입니다. "
            "1.1.5 선동적인 종교 논평 또는 종교 텍스트의 부정확하거나 오해의 소지가 있는 인용. "
            "1.1.6 가짜 위치 추적기 등 허위 정보 및 기능. '오락 목적'이라는 문구로 이 가이드라인을 극복할 수 없습니다. "
            "1.1.7 폭력 충돌, 테러 공격, 전염병 등 최근 사건을 악용하거나 이익을 취하려는 유해한 개념."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "1. Safety",
            "subsection": "1.1 Objectionable Content",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 1.2 사용자 생성 콘텐츠] "
            "사용자 생성 콘텐츠(UGC) 또는 소셜 네트워킹 서비스가 포함된 앱은 다음을 포함해야 합니다: "
            "(a) 부적절한 자료가 앱에 게시되지 않도록 필터링하는 방법 "
            "(b) 불쾌한 콘텐츠를 신고하는 메커니즘과 신속한 대응 "
            "(c) 악용하는 사용자를 차단하는 기능 "
            "(d) 사용자가 쉽게 연락할 수 있는 연락처 정보 공개. "
            "UGC 앱이 주로 음란 콘텐츠, 실제 인물의 대상화, 물리적 위협 또는 괴롭힘에 사용되는 경우 "
            "예고 없이 App Store에서 제거될 수 있습니다. "
            "1.2.1 크리에이터 콘텐츠: 크리에이터 앱은 사용자가 앱의 연령 등급을 초과하는 콘텐츠를 "
            "식별할 수 있는 방법을 제공하고, 인증된 또는 신고된 연령 기반 제한 메커니즘을 사용해야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "1. Safety",
            "subsection": "1.2 User-Generated Content",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 1.3 키즈 카테고리] "
            "키즈 카테고리 앱은 어린이를 위해 설계된 앱을 쉽게 찾을 수 있도록 합니다. "
            "이 앱에는 보호자 게이트 뒤의 지정된 영역에 예약된 경우를 제외하고 "
            "앱 외부 링크, 구매 기회 또는 어린이에 대한 기타 방해 요소를 포함하면 안 됩니다. "
            "키즈 카테고리 앱은 개인 식별 정보 또는 기기 정보를 제3자에게 전송하면 안 됩니다. "
            "제3자 분석 또는 제3자 광고를 포함하면 안 됩니다. "
            "제한된 경우에서 제3자 분석이 허용될 수 있으나, 서비스가 IDFA 또는 어린이의 식별 가능한 정보를 "
            "수집하거나 전송하지 않아야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "1. Safety",
            "subsection": "1.3 Kids Category",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 1.4 신체적 위해] "
            "앱이 신체적 위험을 초래하는 방식으로 작동하면 거부될 수 있습니다. "
            "1.4.1 의료 앱: 부정확한 데이터를 제공할 수 있는 의료 앱은 더 엄격하게 검토됩니다. "
            "건강 측정의 정확성 주장을 뒷받침하는 데이터와 방법론을 명확히 공개해야 합니다. "
            "기기 센서만으로 혈압, 체온, 혈당, 혈중 산소 수준을 측정한다고 주장하는 앱은 허용되지 않습니다. "
            "1.4.2 약물 복용량 계산기: 제약회사, 병원, 대학, 건강보험회사, 약국 또는 FDA 승인 기관에서 제공해야 합니다. "
            "1.4.3 담배, 전자담배, 불법 약물 또는 과도한 알코올 소비를 조장하는 앱은 허용되지 않습니다. "
            "1.4.4 음주운전 검문소 정보는 법 집행 기관이 게시한 것만 표시 가능합니다. "
            "1.4.5 앱은 고객에게 신체적 위험을 초래하는 활동(베팅, 챌린지 등)에 참여하도록 권유하면 안 됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "1. Safety",
            "subsection": "1.4 Physical Harm",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 1.5~1.7] "
            "1.5 개발자 정보: 앱과 지원 URL에 연락 가능한 방법을 포함해야 합니다. "
            "정확하고 최신의 연락처 정보를 포함하지 않으면 일부 국가에서 법을 위반할 수 있습니다. "
            "1.6 데이터 보안: 앱은 Apple Developer Program 라이선스 계약 및 가이드라인에 따라 "
            "수집된 사용자 정보의 적절한 보안 조치를 구현하고, 무단 사용, 공개 또는 제3자의 접근을 방지해야 합니다. "
            "1.7 범죄 활동 신고: 범죄 신고 앱은 현지 법 집행 기관과 관련되어야 하며, "
            "그러한 참여가 활발한 국가 또는 지역에서만 제공할 수 있습니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "1. Safety",
            "subsection": "1.5-1.7 Developer Info, Security, Criminal Activity",
            "effective_date": "2026-01",
        },
    },
    # ── 2. Performance ──
    {
        "text": (
            "[Apple App Store 심사 가이드라인 2.1 앱 완성도] "
            "App Review에 제출하는 앱은 완성된 최종 버전이어야 합니다. 모든 필요한 메타데이터와 기능적 URL이 포함되어야 합니다. "
            "플레이스홀더 텍스트, 빈 웹사이트 및 기타 임시 콘텐츠는 제출 전에 제거해야 합니다. "
            "앱이 로그인을 포함하는 경우 데모 계정 정보를 제공해야 합니다. "
            "불완전한 앱 번들과 충돌하거나 명백한 기술적 문제가 있는 바이너리는 거부됩니다. "
            "2.2 베타 테스팅: 데모, 베타, 시험판은 App Store에 속하지 않습니다. TestFlight를 사용하세요. "
            "TestFlight를 통해 배포되는 앱은 App Review Guidelines를 준수해야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "2. Performance",
            "subsection": "2.1-2.2 Completeness & Beta Testing",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 2.3 정확한 메타데이터] "
            "모든 앱 메타데이터(개인정보 보호 정보, 앱 설명, 스크린샷, 미리보기)는 앱의 핵심 경험을 정확하게 반영해야 합니다. "
            "2.3.1 앱에 숨겨진, 휴면 또는 문서화되지 않은 기능을 포함하면 안 됩니다. "
            "오해를 불러일으키는 마케팅은 앱 제거 또는 개발자 계정 해지의 사유가 됩니다. "
            "2.3.2 인앱 구매가 포함된 경우, 추가 구매가 필요한 항목을 명확히 표시해야 합니다. "
            "2.3.3 스크린샷은 사용 중인 앱을 보여줘야 하며, 단순히 타이틀 아트나 로그인 페이지가 아닌 실제 화면이어야 합니다. "
            "2.3.5 앱에 가장 적합한 카테고리를 선택해야 합니다. "
            "2.3.6 연령 등급 질문에 정직하게 답변하여 앱이 보호자 통제와 적절히 일치하도록 해야 합니다. "
            "2.3.7 고유한 앱 이름(30자 제한)을 선택하고, 앱을 정확히 설명하는 키워드를 지정해야 합니다. "
            "상표, 인기 앱 이름, 가격 정보 또는 기타 무관한 구문으로 메타데이터를 채우지 마세요."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "2. Performance",
            "subsection": "2.3 Accurate Metadata",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 2.4-2.5 하드웨어 및 소프트웨어 요구사항] "
            "2.4 하드웨어 호환성: iPhone 앱은 가능하면 iPad에서도 실행되어야 합니다. "
            "앱은 전력을 효율적으로 사용해야 하며 기기에 손상을 줄 위험이 없어야 합니다. "
            "제3자 광고를 포함한 앱은 암호화폐 채굴 등 관련 없는 백그라운드 프로세스를 실행하면 안 됩니다. "
            "2.5 소프트웨어 요구사항: 앱은 공개 API만 사용하고 현재 출시 OS에서 실행해야 합니다. "
            "2.5.2 앱은 번들에 자체 포함되어야 하며, 코드를 다운로드, 설치, 실행하여 기능을 변경하면 안 됩니다. "
            "2.5.3 바이러스, 파일, 악성 코드를 전송하는 앱은 거부됩니다. "
            "2.5.6 웹 브라우징 앱은 적절한 WebKit 프레임워크를 사용해야 합니다. "
            "2.5.14 앱은 사용자 활동을 기록할 때 명시적 동의와 시각적/청각적 표시를 제공해야 합니다. "
            "2.5.18 디스플레이 광고는 메인 앱 바이너리로 제한되어야 하며, 확장, App Clip, 위젯 등에 포함되면 안 됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "2. Performance",
            "subsection": "2.4-2.5 Hardware & Software Requirements",
            "effective_date": "2026-01",
        },
    },
    # ── 3. Business ──
    {
        "text": (
            "[Apple App Store 심사 가이드라인 3.1.1 인앱 구매] "
            "앱 내에서 기능이나 기능을 잠금 해제하려면(구독, 게임 내 통화, 게임 레벨, 프리미엄 콘텐츠 접근, "
            "전체 버전 잠금 해제 등) 인앱 구매를 사용해야 합니다. "
            "앱은 라이선스 키, QR 코드, 암호화폐 등 자체 메커니즘을 사용하여 콘텐츠나 기능을 잠금 해제하면 안 됩니다. "
            "인앱 구매를 통해 구매한 크레딧이나 게임 내 통화는 만료되면 안 됩니다. "
            "복원 가능한 인앱 구매에 대한 복원 메커니즘이 있어야 합니다. "
            "'전리품 상자' 또는 무작위 가상 항목을 구매하도록 제공하는 메커니즘은 "
            "각 항목 유형을 받을 확률을 구매 전 고객에게 공개해야 합니다. "
            "NFT 관련: 앱은 NFT를 민팅, 목록화, 이전하기 위한 인앱 구매를 사용할 수 있으며, "
            "사용자가 자신의 NFT를 볼 수 있도록 할 수 있으나, "
            "NFT 소유권이 앱 내 기능을 잠금 해제해서는 안 됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "3. Business",
            "subsection": "3.1.1 In-App Purchase",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 3.1.2 구독] "
            "자동 갱신 구독을 제공하는 경우 고객에게 지속적인 가치를 제공해야 하며, "
            "구독 기간은 최소 7일이어야 하고 사용자의 모든 기기에서 사용 가능해야 합니다. "
            "적절한 구독 예시: 새로운 게임 레벨, 에피소드 콘텐츠, 멀티플레이어 지원, "
            "일관적인 대규모 업데이트를 제공하는 앱, 대규모 또는 지속적으로 업데이트되는 미디어 콘텐츠 접근, "
            "SaaS(서비스형 소프트웨어), 클라우드 지원. "
            "구독 기반 비즈니스 모델로 전환하는 경우, 기존 사용자가 이미 결제한 주요 기능을 빼앗아서는 안 됩니다. "
            "사용자를 속여 구독을 구매하게 하거나 미끼 교체 사기를 하는 앱은 App Store에서 제거됩니다. "
            "3.1.2(c) 구독 정보: 고객에게 구독을 요청하기 전에 가격에 대해 사용자가 받을 것을 명확하게 설명해야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "3. Business",
            "subsection": "3.1.2 Subscriptions",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 3.1.3 기타 결제 방법] "
            "다음 앱은 인앱 구매 이외의 결제 방법을 사용할 수 있습니다: "
            "3.1.3(a) '리더' 앱: 잡지, 신문, 책, 오디오, 음악, 비디오 등 이전에 구매한 콘텐츠에 접근 가능. "
            "3.1.3(b) 멀티플랫폼 서비스: 다른 플랫폼이나 웹사이트에서 취득한 콘텐츠, 구독 또는 기능에 접근 가능. "
            "3.1.3(c) 기업 서비스: 조직이나 그룹에 직접 판매하는 앱. "
            "3.1.3(d) 개인 간 서비스: 두 개인 간의 실시간 서비스(튜터링, 의료 상담, 부동산 투어, 피트니스 트레이닝). "
            "3.1.3(e) 앱 외부 상품 및 서비스: 앱 외부에서 소비되는 물리적 상품이나 서비스 구매. "
            "3.1.3(f) 무료 독립형 앱: 유료 웹 기반 도구의 무료 독립형 동반자 앱. "
            "3.1.5 암호화폐: 지갑 앱은 조직으로 등록된 개발자만 제공 가능. "
            "앱에서 암호화폐 채굴 불가(오프디바이스 제외). 거래소는 적절한 라이선스가 필요합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "3. Business",
            "subsection": "3.1.3-3.1.5 Other Payment Methods & Crypto",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 3.2 기타 비즈니스 모델 이슈] "
            "3.2.1 허용: 자체 앱 홍보(카탈로그 전용 앱 제외), 제3자 앱 컬렉션 표시(적절한 에디토리얼 콘텐츠 포함), "
            "보험 앱(무료, 인앱 구매 사용 불가), 비영리 단체의 직접 모금(Apple Pay 지원 필수). "
            "3.2.2 불허: App Store와 유사한 제3자 앱 표시 인터페이스 생성, "
            "광고 노출 수나 클릭 수를 인위적으로 증가, 자선 단체를 위한 앱 내 모금(승인된 비영리 제외), "
            "위치 또는 이동통신사로 앱 사용 임의 제한, "
            "바이너리 옵션 거래 앱 불허, CFD/외환 앱은 적절한 라이선스 필요, "
            "개인 대출 앱은 최대 APR 36% 이하, 60일 이하 전액 상환 불허. "
            "앱 평가, 리뷰, 다른 앱 다운로드를 강제해서는 안 됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "3. Business",
            "subsection": "3.2 Other Business Model Issues",
            "effective_date": "2026-01",
        },
    },
    # ── 4. Design ──
    {
        "text": (
            "[Apple App Store 심사 가이드라인 4.1 카피캣] "
            "4.1(a) 자신만의 아이디어를 개발하세요. App Store의 최신 인기 앱을 단순히 복사하거나, "
            "다른 앱의 이름이나 UI를 약간 변경하여 자신의 것으로 내세우지 마세요. "
            "지적재산권 침해 위험뿐 아니라 App Store 탐색이 어려워지고 동료 개발자에게 불공평합니다. "
            "4.1(b) 다른 앱이나 서비스를 사칭하는 앱 제출은 개발자 행동 규범 위반으로 간주되며 "
            "Apple Developer Program에서 제거될 수 있습니다. "
            "4.1(c) 다른 개발자의 아이콘, 브랜드 또는 제품 이름을 해당 개발자의 승인 없이 사용할 수 없습니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "4. Design",
            "subsection": "4.1 Copycats",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 4.2 최소 기능] "
            "앱은 리패키지된 웹사이트 이상의 기능, 콘텐츠, UI를 포함해야 합니다. "
            "특별히 유용하지 않거나 독특하지 않거나 '앱다운' 것이 아니라면 App Store에 속하지 않습니다. "
            "지속적인 엔터테인먼트 가치나 적절한 유틸리티를 제공하지 않는 앱은 수락되지 않을 수 있습니다. "
            "4.2.2 카탈로그를 제외하고, 앱은 주로 마케팅 자료, 광고, 웹 클리핑, "
            "콘텐츠 집합기 또는 링크 모음이어서는 안 됩니다. "
            "4.2.6 상용화된 템플릿이나 앱 생성 서비스로 만든 앱은 거부됩니다. "
            "템플릿 제공자가 콘텐츠 제공자를 대신하여 직접 제출하는 경우는 허용됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "4. Design",
            "subsection": "4.2 Minimum Functionality",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 4.3 스팸 / 4.7 미니 앱 / 4.8 로그인 서비스] "
            "4.3 스팸: 동일한 앱의 여러 번들 ID를 만들지 마세요. 다양한 버전이 필요한 경우 "
            "단일 앱을 제출하고 인앱 구매로 변형을 제공하세요. "
            "이미 포화된 카테고리에 추가하지 마세요. 스토어 스팸은 Apple Developer Program에서 제거될 수 있습니다. "
            "4.7 미니 앱, 스트리밍 게임, 챗봇, 플러그인, 게임 에뮬레이터: "
            "앱은 HTML5/JavaScript 미니 앱, 스트리밍 게임, 챗봇, 플러그인, 레트로 게임 에뮬레이터를 제공할 수 있습니다. "
            "모든 소프트웨어가 가이드라인과 관련 법률을 준수해야 합니다. "
            "4.8 로그인 서비스: 제3자 소셜 로그인 서비스를 사용하는 앱은 "
            "동등한 옵션으로 데이터 수집을 이름과 이메일로 제한하고, "
            "이메일 비공개 옵션을 제공하며, 동의 없이 앱 상호작용 데이터를 광고 목적으로 수집하지 않는 "
            "다른 로그인 서비스도 제공해야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "4. Design",
            "subsection": "4.3 Spam / 4.7 Mini Apps / 4.8 Login",
            "effective_date": "2026-01",
        },
    },
    # ── 5. Legal ──
    {
        "text": (
            "[Apple App Store 심사 가이드라인 5.1.1 데이터 수집 및 저장] "
            "모든 앱은 App Store Connect 메타데이터 필드와 앱 내에서 쉽게 접근 가능한 방식으로 "
            "개인정보 보호 정책 링크를 포함해야 합니다. 개인정보 보호 정책은 다음을 명확하고 명시적으로 해야 합니다: "
            "(1) 앱/서비스가 수집하는 데이터, 수집 방법 및 모든 용도를 식별 "
            "(2) 사용자 데이터를 공유하는 제3자가 동일한 보호를 제공함을 확인 "
            "(3) 데이터 보존/삭제 정책을 설명하고 사용자가 동의를 철회하거나 데이터 삭제를 요청하는 방법 설명. "
            "권한: 데이터를 수집하는 앱은 수집이 익명으로 간주되더라도 사용자 동의를 확보해야 합니다. "
            "데이터 최소화: 앱은 핵심 기능에 관련된 데이터에만 접근을 요청해야 합니다. "
            "접근: 앱은 사용자의 권한 설정을 존중하고 불필요한 데이터 접근에 동의하도록 조작하면 안 됩니다. "
            "계정 로그인: 주요 계정 기반 기능이 없으면 로그인 없이 사용할 수 있어야 합니다. "
            "계정 생성을 지원하는 경우 앱 내에서 계정 삭제도 제공해야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "5. Legal",
            "subsection": "5.1.1 Data Collection and Storage",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 5.1.2 데이터 사용 및 공유] "
            "법으로 허용되지 않는 한, 먼저 허가를 받지 않고 개인 데이터를 사용, 전송 또는 공유하면 안 됩니다. "
            "개인 데이터가 제3자 AI를 포함한 제3자와 공유되는 위치를 명확하게 공개하고 "
            "명시적 허가를 받아야 합니다. "
            "App Tracking Transparency API를 통해 사용자의 명시적 허가를 받아야 추적이 가능합니다. "
            "한 목적으로 수집된 데이터는 추가 동의 없이 재사용할 수 없습니다. "
            "앱은 수집된 데이터를 기반으로 사용자 프로필을 은밀하게 구축하면 안 됩니다. "
            "연락처, 사진 또는 기타 사용자 데이터 API의 정보를 자체 사용이나 제3자 판매/배포를 위한 "
            "연락처 데이터베이스 구축에 사용하면 안 됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "5. Legal",
            "subsection": "5.1.2 Data Use and Sharing",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 5.1.3-5.1.5 건강/어린이/위치] "
            "5.1.3 건강 및 건강 연구: 건강, 피트니스, 의료 데이터는 특히 민감합니다. "
            "HealthKit API, Clinical Health Records API 등에서 수집된 데이터는 "
            "광고, 마케팅 또는 데이터 마이닝 목적으로 사용하거나 제3자에게 공개하면 안 됩니다. "
            "5.1.4 어린이: 어린이의 개인 데이터를 다룰 때 COPPA, GDPR 등 관련 법률을 준수해야 합니다. "
            "어린이 대상 앱은 제3자 분석이나 제3자 광고를 포함하면 안 됩니다. "
            "5.1.5 위치 서비스: 앱이 제공하는 기능과 서비스에 직접 관련된 경우에만 위치 서비스를 사용해야 합니다. "
            "위치 데이터를 수집, 전송 또는 사용하기 전에 알리고 동의를 받아야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "5. Legal",
            "subsection": "5.1.3-5.1.5 Health, Kids, Location",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 5.2 지적재산권] "
            "5.2.1 일반: 앱에 허가 없이 상표, 저작물, 특허 아이디어 등 보호된 제3자 자료를 사용하지 마세요. "
            "오해의 소지가 있는 표현, 이름, 메타데이터를 포함하지 마세요. "
            "5.2.2 제3자 사이트/서비스: 앱이 제3자 서비스의 콘텐츠를 사용, 접근, 수익화하거나 표시하는 경우 "
            "서비스 이용 약관에 따라 허용되는지 확인해야 합니다. "
            "5.2.3 오디오/비디오 다운로드: 앱은 제3자 소스(Apple Music, YouTube, SoundCloud, Vimeo 등)에서 "
            "명시적 허가 없이 미디어를 저장, 변환, 다운로드하는 기능을 포함하면 안 됩니다. "
            "5.3 게임, 도박, 복권: 실제 돈이 관련된 게임(스포츠 베팅, 포커, 카지노, 경마)이나 복권은 "
            "필요한 라이선스와 권한이 있어야 하며, 해당 지역으로 제한되어야 하고, App Store에서 무료여야 합니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "5. Legal",
            "subsection": "5.2-5.3 IP, Gaming, Gambling",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Apple App Store 심사 가이드라인 5.4-5.5 VPN 및 MDM] "
            "5.4 VPN 앱: NEVPNManager API를 사용해야 하며 조직으로 등록된 개발자만 제공 가능합니다. "
            "어떤 사용자 데이터가 수집되고 어떻게 사용되는지 명확하게 선언해야 합니다. "
            "VPN 앱은 어떤 목적으로든 제3자에게 데이터를 판매, 사용 또는 공개하면 안 됩니다. "
            "VPN 라이선스가 필요한 지역에서는 라이선스 정보를 App Review 메모에 제공해야 합니다. "
            "5.5 모바일 기기 관리(MDM): MDM 서비스를 제공하는 앱은 Apple에 기능을 요청해야 합니다. "
            "상업 기업, 교육 기관 또는 정부 기관만 제공할 수 있습니다. "
            "어떤 사용자 데이터가 수집되고 사용되는지 명확히 선언해야 합니다. "
            "MDM 앱은 제3자에게 데이터를 판매, 사용 또는 공개하면 안 됩니다."
        ),
        "metadata": {
            "store": "apple",
            "policy_name": "App Store Review Guidelines",
            "section": "5. Legal",
            "subsection": "5.4-5.5 VPN and MDM",
            "effective_date": "2026-01",
        },
    },
]

# ─────────────────────────────────────────────────────────────
# Google Play Developer Program Policy
# ─────────────────────────────────────────────────────────────

GOOGLE_POLICIES: list[dict] = [
    # ── Restricted Content ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 제한된 콘텐츠: 아동 안전] "
            "Google Play에서는 아동을 위험에 빠뜨리는 앱을 엄격히 금지합니다. "
            "아동 성적 학대 자료(CSAM)를 생성, 업로드 또는 배포하는 앱은 즉시 삭제되고 "
            "관련 당국에 신고됩니다. "
            "아동을 대상으로 하는 앱은 적절한 연령 등급을 설정해야 하며, "
            "아동의 개인 정보를 무단으로 수집하면 안 됩니다. "
            "매칭메이킹, 데이팅 또는 도박 기능이 있는 앱은 Play Console 도구를 사용하여 "
            "미성년자의 접근을 차단해야 합니다(2025년 10월 정책 업데이트). "
            "2026년 1월 1일부터 개발자는 Age Signals API의 데이터를 "
            "앱 내 연령 적합 경험을 제공하는 용도로만 사용할 수 있습니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Restricted Content",
            "subsection": "Child Safety",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 제한된 콘텐츠: 부적절한 콘텐츠] "
            "Google Play에서는 다음 유형의 콘텐츠를 포함하는 앱을 허용하지 않습니다: "
            "(1) 성적으로 노골적인 콘텐츠: 포르노그래피 또는 성적 만족을 목적으로 한 콘텐츠. "
            "성적 콘텐츠가 포함된 앱은 적절한 콘텐츠 등급을 적용해야 합니다. "
            "(2) 증오 표현: 인종, 민족, 종교, 장애, 성별, 연령, 국적, 성적 지향 등을 이유로 "
            "폭력을 조장하거나 증오를 선동하는 콘텐츠. "
            "(3) 폭력: 불필요하게 잔인하거나 폭력적인 콘텐츠. 실제 폭력의 사실적 묘사는 허용되지 않습니다. "
            "(4) 괴롭힘 및 따돌림: 다른 사용자를 괴롭히거나, 위협하거나, 따돌리는 콘텐츠를 포함하거나 촉진하는 앱. "
            "(5) 위험한 제품: 폭발물, 총기, 탄약 또는 특정 무기 액세서리의 판매를 촉진하는 앱."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Restricted Content",
            "subsection": "Inappropriate Content",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 제한된 콘텐츠: 금융/도박/불법] "
            "금융 서비스: 개인 대출 앱은 투명한 공개가 필요합니다. "
            "60일 이내 전액 상환을 요구하는 단기 개인 대출 앱은 허용되지 않습니다. "
            "인도에서는 정부 승인 디지털 대출 목록에 부합해야 합니다. "
            "실제 돈 도박: 온라인 도박 앱은 적절한 라이선스를 보유하고 해당 관할권으로 제한되어야 합니다. "
            "미성년자를 대상으로 하면 안 됩니다. 도박 관련 앱은 책임 도박 정보를 포함해야 합니다. "
            "불법 활동: 불법 활동을 조장하거나 촉진하는 앱은 허용되지 않습니다. "
            "마리화나: 합법적 관할권에서도 Google Play에서 마리화나 판매를 촉진하는 앱은 허용되지 않습니다. "
            "건강 관련 콘텐츠: 건강 앱은 정보 출처를 검증하고 근거 없는 주장을 피해야 합니다. "
            "AI 생성 콘텐츠: AI 생성 요소에 대한 공개가 필요하며, 허위 정보 확산을 방지해야 합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Restricted Content",
            "subsection": "Financial Services, Gambling, Illegal Activities",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 제한된 콘텐츠: UGC 및 블록체인] "
            "사용자 생성 콘텐츠(UGC): UGC가 포함된 앱은 다음을 구현해야 합니다: "
            "(1) 부적절한 UGC를 필터링하는 시스템 "
            "(2) 불쾌한 콘텐츠 신고 메커니즘 "
            "(3) 불량 사용자를 차단하는 기능 "
            "(4) UGC가 앱의 주요 목적이 아닌 경우에도 이러한 보호 장치가 필요합니다. "
            "증강현실(AR) 앱의 경우, UGC 관리는 부적절한 AR UGC와 민감한 AR 앵커링 위치 "
            "(군사 기지, 사유재산 등)를 모두 고려해야 합니다. "
            "성적 콘텐츠가 '부수적'으로 나타나는 경우, 앱이 주로 비성적 콘텐츠를 제공하고 "
            "적극적으로 홍보하지 않는 한 허용될 수 있습니다. "
            "블록체인 기반 콘텐츠: NFT 지원 앱은 Google Play의 결제 정책을 준수해야 합니다. "
            "토큰화된 디지털 자산의 경우 적절한 공개가 필요합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Restricted Content",
            "subsection": "User-Generated Content & Blockchain",
            "effective_date": "2026-01",
        },
    },
    # ── Privacy, Deception and Device Abuse ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 개인정보, 기만, 기기 악용: 사용자 데이터] "
            "모든 앱은 개인정보 보호 정책을 포함해야 하며, 개인 및 민감한 사용자 데이터의 "
            "접근, 수집, 사용, 공유를 포괄적으로 공개해야 합니다. "
            "개인 및 민감한 사용자 데이터에는 다음이 포함됩니다: "
            "개인 식별 정보, 금융 및 결제 정보, 인증 정보, 전화번호부, 연락처, "
            "기기 위치, SMS/통화 관련 데이터, 건강 데이터, "
            "기기의 다른 앱 목록, 마이크/카메라 및 기타 민감한 기기 데이터. "
            "앱은 데이터 안전 섹션을 정확하게 완성해야 합니다. "
            "카메라 및 갤러리 접근이 필요한 앱은 접근 필요성을 정당화하고 "
            "미디어를 책임감 있게 처리해야 합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Privacy, Deception and Device Abuse",
            "subsection": "User Data",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 개인정보, 기만, 기기 악용: 기만적 행위] "
            "Google Play에서는 사용자를 기만하는 앱을 허용하지 않습니다. "
            "기만적 행위의 예시: "
            "(1) 기능이나 콘텐츠에 대해 허위 또는 오해의 소지가 있는 설명 제공 "
            "(2) 앱의 기능에 대해 사용자를 오도하는 인터페이스 설계 "
            "(3) 다른 앱이나 서비스로 가장하는 앱(사칭) "
            "(4) 소셜 엔지니어링 기법을 사용하여 민감한 정보를 수집하는 앱 "
            "(5) 허위 또는 검증되지 않은 주장으로 기기 보안이나 성능에 대해 불안감을 조성하는 앱 "
            "네트워크 또는 기기에 대한 무단 접근을 용이하게 하는 앱은 금지됩니다. "
            "조작된 미디어: 기만적 목적으로 딥페이크 또는 조작된 미디어를 생성하는 앱은 허용되지 않습니다. "
            "투명성: 앱은 사용자에게 수행하는 작업에 대해 투명해야 합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Privacy, Deception and Device Abuse",
            "subsection": "Deceptive Behavior",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 기기 및 네트워크 악용] "
            "사용자의 기기, 다른 기기, 컴퓨터, 서버, 네트워크, API 또는 서비스를 "
            "방해하거나 접근하거나 손상시키는 앱은 허용되지 않습니다. "
            "이에는 기기의 다른 앱, Google 서비스, 인증된 이동통신사 네트워크가 포함됩니다. "
            "금지 행위: "
            "(1) 광고를 표시하는 앱 또는 서비스의 작동을 방해하는 행위 "
            "(2) 다른 앱에 광고를 표시하는 프록시 또는 리디렉션 트래픽 "
            "(3) 게임 치트 생성 또는 배포 "
            "(4) 통신 서비스에 대한 무단 접근 촉진 "
            "(5) 사용자 동의 없이 기기에서 데이터를 전송하는 스파이웨어 "
            "(6) VPN 연결을 통해 광고 클릭/노출을 리디렉션 또는 조작하는 앱. "
            "백그라운드에서 실행되는 앱은 사용자에게 명확하게 공개해야 합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Privacy, Deception and Device Abuse",
            "subsection": "Device and Network Abuse",
            "effective_date": "2026-01",
        },
    },
    # ── Intellectual Property ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 지적재산권] "
            "다른 사람의 지적재산권을 침해하는 앱이나 개발자 계정은 허용되지 않습니다. "
            "여기에는 상표권, 저작권, 특허권, 영업비밀 및 기타 독점적 권리가 포함됩니다. "
            "저작권 침해: 저작권으로 보호되는 콘텐츠를 무단으로 복제, 배포, 표시하는 앱은 금지됩니다. "
            "상표 침해: 다른 브랜드의 상표를 오해의 소지가 있는 방식으로 사용하는 앱은 금지됩니다. "
            "위조품: 가짜 상품의 판매를 촉진하거나 다른 브랜드와의 제휴를 허위로 암시하는 앱은 허용되지 않습니다. "
            "지적재산권 침해 신고를 받으면 Google은 해당 앱을 검토하고 적절한 조치를 취합니다. "
            "반복적인 위반은 개발자 계정 정지로 이어질 수 있습니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Intellectual Property",
            "subsection": "Copyright, Trademark, Counterfeit",
            "effective_date": "2026-01",
        },
    },
    # ── Monetization and Ads ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 수익화 및 광고: 결제] "
            "Google Play 결제 시스템: 앱 내에서 디지털 상품 또는 서비스를 판매하는 경우 "
            "Google Play 결제 시스템을 사용해야 합니다. "
            "미국 내에서는 Epic Games 판결에 따라 2025년 10월 29일부터 "
            "개발자가 외부 다운로드 또는 거래로 연결하거나 대체 결제 방법을 제공할 수 있습니다. "
            "개발자는 2026년 1월 28일까지 이러한 정책을 준수해야 합니다. "
            "구독: 자동 갱신 구독은 투명한 가격 정보를 제공해야 합니다. "
            "무료 체험 후 자동 청구되는 경우 사전에 명확히 고지해야 합니다. "
            "사용자가 구독을 쉽게 취소할 수 있어야 합니다. "
            "로열티 프로그램 혜택은 앱 내 적격 금전적 거래에 부수적이어야 하며, "
            "실제 돈 도박 정책을 위반하는 교환 방식에 연결되면 안 됩니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Monetization and Ads",
            "subsection": "Payments and Subscriptions",
            "effective_date": "2026-01",
        },
    },
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 수익화 및 광고: 광고 정책] "
            "광고를 표시하는 앱은 다음 규칙을 준수해야 합니다: "
            "(1) 광고는 앱의 기능을 방해하거나 사용자 경험을 저해하면 안 됩니다. "
            "(2) 전면 광고(interstitial)는 쉽게 닫을 수 있어야 합니다. "
            "(3) 잠금 화면 광고: 기기 잠금 화면에 광고를 표시하는 앱은 허용되지 않습니다. "
            "(4) 기만적 광고: 시스템 알림이나 경고처럼 보이는 광고는 금지됩니다. "
            "(5) 아동 대상 광고: 어린이용 앱의 광고는 관련 규정을 준수해야 합니다. "
            "(6) 광고 주도 앱: 주로 광고 표시를 목적으로 하는 앱은 허용되지 않습니다. "
            "(7) 보상형 광고: 사용자에게 보상을 제공하는 광고는 명확하게 표시되어야 합니다. "
            "앱은 광고 SDK가 이러한 정책을 준수하도록 해야 합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Monetization and Ads",
            "subsection": "Ads Policy",
            "effective_date": "2026-01",
        },
    },
    # ── Store Listing and Promotion ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 스토어 목록 및 홍보] "
            "앱의 스토어 목록은 사용자에게 앱의 기능과 콘텐츠를 정확하게 전달해야 합니다. "
            "금지 사항: "
            "(1) 오해의 소지가 있는 앱 제목, 아이콘 또는 설명 "
            "(2) 앱의 기능이나 콘텐츠를 허위로 표현하는 스크린샷 또는 동영상 "
            "(3) 허위 또는 오해의 소지가 있는 성능 주장 "
            "(4) 다른 앱이나 서비스와의 허위 제휴 또는 보증 표시 "
            "(5) 키워드 스팸: 무관한 키워드를 메타데이터에 포함하는 행위 "
            "(6) 허위 또는 조작된 리뷰 및 평점 "
            "(7) 인위적으로 다운로드 수나 순위를 높이는 행위 "
            "개발자는 앱의 콘텐츠 등급을 정확하게 설정해야 합니다. "
            "부적절한 콘텐츠 등급은 앱 삭제로 이어질 수 있습니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Store Listing and Promotion",
            "subsection": "Metadata, Ratings, Reviews",
            "effective_date": "2026-01",
        },
    },
    # ── Spam, Functionality ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 스팸 및 기능] "
            "스팸: Google Play에서는 반복적이거나 품질이 낮은 앱을 허용하지 않습니다. "
            "금지 사항: "
            "(1) 동일하거나 유사한 콘텐츠를 가진 여러 앱 제출 "
            "(2) 주로 텍스트나 PDF 파일로 구성된 앱으로 최소한의 기능만 제공하는 경우 "
            "(3) 사용자 가치를 거의 제공하지 않는 앱의 대량 생성 "
            "(4) 주로 광고 표시를 목적으로 하는 앱 "
            "기능 요구사항: "
            "(1) 앱은 안정적이고 반응성이 있으며 기능적이어야 합니다. "
            "(2) 앱이 충돌하거나, 강제 종료되거나, 정지되거나, 비정상적으로 작동하면 안 됩니다. "
            "(3) 과도한 광고가 앱의 성능을 저하시키면 안 됩니다. "
            "새로운 앱은 프로덕션 출시 전 최소 12명의 테스터와 14일간의 테스트가 필요합니다(2026년 정책)."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Spam and Functionality",
            "subsection": "Spam, Minimum Functionality",
            "effective_date": "2026-01",
        },
    },
    # ── Malware & Unwanted Software ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 악성 소프트웨어 및 원치 않는 소프트웨어] "
            "악성 소프트웨어(멀웨어): Google Play에서는 사용자의 기기, 데이터 또는 네트워크를 "
            "손상시킬 수 있는 앱을 엄격히 금지합니다. "
            "금지되는 악성 소프트웨어 유형: "
            "(1) 트로이 목마: 합법적으로 보이지만 악의적인 작업을 수행하는 앱 "
            "(2) 스파이웨어: 사용자 동의 없이 개인 데이터를 수집하거나 전송하는 앱 "
            "(3) 랜섬웨어: 사용자의 기기나 데이터를 제어하고 몸값을 요구하는 앱 "
            "(4) 백도어: 기기에서 무단 원격 제어 작업을 수행할 수 있게 하는 앱 "
            "원치 않는 소프트웨어(MUwS): "
            "(1) 사용자에 대해 투명하지 않고 예상과 다르게 작동하는 소프트웨어 "
            "(2) 사용자가 원하지 않는 방식으로 시스템 상태에 영향을 미치는 소프트웨어 "
            "(3) 제거하기 어려운 소프트웨어 "
            "사칭(Impersonation): 다른 앱이나 개발자를 사칭하여 사용자를 속이는 앱은 금지됩니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Malware and Mobile Unwanted Software",
            "subsection": "Malware, MUwS, Impersonation",
            "effective_date": "2026-01",
        },
    },
    # ── SDK Requirements ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - SDK 사용 요구사항] "
            "앱에 포함된 SDK(소프트웨어 개발 키트)도 Google Play 정책을 준수해야 합니다. "
            "개발자는 앱에 포함된 모든 SDK의 동작에 대해 책임을 집니다. "
            "SDK 요구사항: "
            "(1) SDK는 사용자 데이터를 허가 없이 수집하거나 전송하면 안 됩니다. "
            "(2) SDK는 사용자의 기기 성능에 부정적인 영향을 미치면 안 됩니다. "
            "(3) SDK가 광고를 표시하는 경우, Google Play의 광고 정책을 준수해야 합니다. "
            "(4) SDK를 통해 수집된 데이터의 처리도 개인정보 보호 정책에 포함되어야 합니다. "
            "개발자 인증: 2026년부터 단계적으로 모든 앱은 인증된 개발자가 등록해야 합니다. "
            "브라질, 인도네시아, 싱가포르에서 2026년 9월에 시작되어 2027년에 전면 시행됩니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Use of SDKs In Apps",
            "subsection": "SDK Requirements and Developer Verification",
            "effective_date": "2026-01",
        },
    },
    # ── Families ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 가족 프로그램] "
            "Google Play의 가족 정책은 어린이와 가족을 대상으로 하는 앱에 대한 "
            "추가 요구사항을 규정합니다. "
            "가족용 앱 요구사항: "
            "(1) COPPA(아동 온라인 프라이버시 보호법) 준수 "
            "(2) 적절한 콘텐츠 등급 설정 "
            "(3) 어린이에게 부적절한 광고 표시 금지 "
            "(4) 광고는 Google의 가족용 광고 정책을 준수해야 합니다 "
            "(5) 어린이의 개인 정보 수집 제한 "
            "(6) 앱이 어린이의 관심사를 추적하거나 프로파일링하면 안 됩니다 "
            "Teacher Approved 프로그램: 교육 가치가 있는 앱을 위한 추가 인증 프로그램으로, "
            "교육 전문가가 앱의 품질과 적합성을 검토합니다. "
            "연령에 적합한 경험을 제공하기 위해 Age Signals API를 활용할 수 있습니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Families",
            "subsection": "Kids and Family Policy",
            "effective_date": "2026-01",
        },
    },
    # ── Enforcement ──
    {
        "text": (
            "[Google Play 개발자 프로그램 정책 - 시행] "
            "Google Play는 정책 위반에 대해 다음과 같은 조치를 취할 수 있습니다: "
            "(1) 경고: 경미한 위반에 대해 경고를 발행하고 시정 기회를 제공합니다. "
            "(2) 앱 삭제: 정책을 위반하는 앱은 Google Play에서 삭제됩니다. "
            "(3) 앱 정지: 심각한 위반의 경우 앱이 정지될 수 있습니다. "
            "(4) 개발자 계정 해지: 반복적이거나 심각한 위반은 개발자 계정 해지로 이어집니다. "
            "(5) 법적 조치: 범죄 활동이 의심되는 경우 관련 당국에 신고합니다. "
            "이의 신청: 개발자는 Google Play의 결정에 대해 이의를 신청할 수 있습니다. "
            "정책 변경: Google은 정기적으로 정책을 업데이트하며, "
            "개발자에게 변경 사항과 준수 기한을 사전에 통지합니다. "
            "Android 인증: 모든 앱은 인증된 Android 기기에 설치되기 위해 "
            "인증된 개발자가 등록해야 합니다."
        ),
        "metadata": {
            "store": "google",
            "policy_name": "Google Play Developer Program Policy",
            "section": "Enforcement",
            "subsection": "Violations and Actions",
            "effective_date": "2026-01",
        },
    },
]


def get_all_store_policies() -> list[dict]:
    """Apple + Google 전체 스토어 정책 데이터 반환"""
    return APPLE_POLICIES + GOOGLE_POLICIES
