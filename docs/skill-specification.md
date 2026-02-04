# Claude Code Skill 명세서

**작성일:** 2026-01-31  
**총 Skill 수:** 21개  
**저장 위치:** `C:\Users\tlduf\.cursor\skills-cursor\`

---

## 목차

1. [문서 처리 (Document)](#1-문서-처리-document)
2. [디자인 & 크리에이티브 (Design)](#2-디자인--크리에이티브-design)
3. [개발 도구 (Development)](#3-개발-도구-development)
4. [테스트 & 자동화 (Testing)](#4-테스트--자동화-testing)
5. [커뮤니케이션 (Communication)](#5-커뮤니케이션-communication)

---

## 1. 문서 처리 (Document)

### 1.1 docx
| 항목 | 내용 |
|------|------|
| **이름** | docx |
| **용도** | Word 문서(.docx) 생성, 편집, 분석 |
| **트리거** | Word 문서 작업, 추적 변경, 주석 추가, 서식 유지 |
| **주요 기능** | 새 문서 생성, 콘텐츠 수정, Tracked Changes, 주석 추가 |
| **기술** | OOXML, ZIP 아카이브 기반 XML 처리 |

### 1.2 pdf
| 항목 | 내용 |
|------|------|
| **이름** | pdf |
| **용도** | PDF 문서 처리 및 조작 |
| **트리거** | PDF 폼 작성, 문서 생성/병합/분할, 텍스트 추출 |
| **주요 기능** | 텍스트/테이블 추출, PDF 생성, 병합/분할, 폼 처리 |
| **기술** | pypdf, Python 라이브러리 |

### 1.3 pptx
| 항목 | 내용 |
|------|------|
| **이름** | pptx |
| **용도** | PowerPoint 프레젠테이션 생성, 편집, 분석 |
| **트리거** | 프레젠테이션 작업, 레이아웃, 발표자 노트, 주석 |
| **주요 기능** | 슬라이드 생성/편집, 레이아웃 작업, 발표자 노트 |
| **기술** | OOXML, markitdown 변환 |

### 1.4 xlsx
| 항목 | 내용 |
|------|------|
| **이름** | xlsx |
| **용도** | Excel 스프레드시트 생성, 편집, 분석 |
| **트리거** | 스프레드시트 작업, 수식, 데이터 분석, 시각화 |
| **주요 기능** | 수식 처리, 서식 지정, 데이터 분석, 차트 생성 |
| **표준** | 금융 모델 색상 코딩 (Blue=입력, Black=수식, Green=내부링크) |

---

## 2. 디자인 & 크리에이티브 (Design)

### 2.1 frontend-design
| 항목 | 내용 |
|------|------|
| **이름** | frontend-design |
| **용도** | 고품질 프론트엔드 UI 디자인 |
| **트리거** | 웹 컴포넌트, 페이지, 대시보드, React, HTML/CSS 레이아웃 |
| **주요 기능** | 프로덕션급 인터페이스, 독창적 디자인, AI 슬롭 회피 |
| **철학** | 과감한 미적 방향, 의도적 디자인, 독특한 타이포그래피 |

### 2.2 canvas-design
| 항목 | 내용 |
|------|------|
| **이름** | canvas-design |
| **용도** | 시각 아트 및 디자인 생성 (.png, .pdf) |
| **트리거** | 포스터, 아트, 디자인, 정적 비주얼 제작 |
| **주요 기능** | 디자인 철학 생성 → 캔버스 표현 (2단계 워크플로우) |
| **출력** | .md (철학), .pdf, .png 파일 |

### 2.3 algorithmic-art
| 항목 | 내용 |
|------|------|
| **이름** | algorithmic-art |
| **용도** | p5.js 기반 알고리즘 아트 생성 |
| **트리거** | 제너레이티브 아트, 플로우 필드, 파티클 시스템 |
| **주요 기능** | 알고리즘 철학 생성 → p5.js 표현 (2단계 워크플로우) |
| **출력** | .md (철학), .html (뷰어), .js (알고리즘) |

### 2.4 brand-guidelines
| 항목 | 내용 |
|------|------|
| **이름** | brand-guidelines |
| **용도** | Anthropic 브랜드 스타일 적용 |
| **트리거** | 브랜드 컬러, 스타일 가이드라인, 비주얼 포맷팅 |
| **주요 색상** | Dark: #141413, Light: #faf9f5, Orange: #d97757, Blue: #6a9bcc |

### 2.5 theme-factory
| 항목 | 내용 |
|------|------|
| **이름** | theme-factory |
| **용도** | 아티팩트에 테마 스타일링 적용 |
| **트리거** | 슬라이드, 문서, HTML 페이지 스타일링 |
| **주요 기능** | 10개 프리셋 테마 (색상 팔레트 + 폰트 페어링) |

### 2.6 slack-gif-creator
| 항목 | 내용 |
|------|------|
| **이름** | slack-gif-creator |
| **용도** | Slack 최적화 애니메이션 GIF 생성 |
| **트리거** | "Slack용 X GIF 만들어줘" |
| **사양** | Emoji: 128x128, Message: 480x480, FPS: 10-30 |

---

## 3. 개발 도구 (Development)

### 3.1 create-skill
| 항목 | 내용 |
|------|------|
| **이름** | create-skill |
| **용도** | Cursor용 Agent Skill 생성 가이드 |
| **트리거** | skill 생성, SKILL.md 작성, skill 구조 |
| **저장 위치** | 개인: `~/.cursor/skills/`, 프로젝트: `.cursor/skills/` |

### 3.2 skill-creator
| 항목 | 내용 |
|------|------|
| **이름** | skill-creator |
| **용도** | 효과적인 skill 생성 상세 가이드 |
| **트리거** | 새 skill 생성, 기존 skill 업데이트 |
| **원칙** | 컨텍스트 윈도우 효율성, 모듈화, 재사용성 |

### 3.3 create-rule
| 항목 | 내용 |
|------|------|
| **이름** | create-rule |
| **용도** | Cursor 규칙 생성 (지속적 AI 가이드) |
| **트리거** | 코딩 표준, 프로젝트 컨벤션, RULE.md 생성 |
| **저장 위치** | `.cursor/rules/` |

### 3.4 create-subagent
| 항목 | 내용 |
|------|------|
| **이름** | create-subagent |
| **용도** | 커스텀 서브에이전트 생성 |
| **트리거** | 태스크별 에이전트, 코드 리뷰어, 디버거, 도메인 전문 어시스턴트 |
| **저장 위치** | 프로젝트: `.cursor/agents/`, 개인: `~/.cursor/agents/` |

### 3.5 migrate-to-skills
| 항목 | 내용 |
|------|------|
| **이름** | migrate-to-skills |
| **용도** | Cursor 규칙/명령어를 Skill로 변환 |
| **소스** | `.cursor/rules/*.mdc`, `.cursor/commands/*.md` |
| **대상** | `.cursor/skills/` |

### 3.6 mcp-builder
| 항목 | 내용 |
|------|------|
| **이름** | mcp-builder |
| **용도** | MCP (Model Context Protocol) 서버 개발 가이드 |
| **트리거** | MCP 서버 구축, 외부 API/서비스 통합 |
| **지원** | Python (FastMCP), Node/TypeScript (MCP SDK) |

### 3.7 update-cursor-settings
| 항목 | 내용 |
|------|------|
| **이름** | update-cursor-settings |
| **용도** | Cursor/VSCode 사용자 설정 수정 |
| **트리거** | 에디터 설정, 테마, 폰트 크기, 자동 저장 |
| **파일** | Windows: `%APPDATA%\Cursor\User\settings.json` |

### 3.8 web-artifacts-builder
| 항목 | 내용 |
|------|------|
| **이름** | web-artifacts-builder |
| **용도** | 복잡한 HTML 아티팩트 빌드 |
| **트리거** | 상태 관리, 라우팅, shadcn/ui 컴포넌트 필요 시 |
| **스택** | React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui |

---

## 4. 테스트 & 자동화 (Testing)

### 4.1 webapp-testing
| 항목 | 내용 |
|------|------|
| **이름** | webapp-testing |
| **용도** | 로컬 웹앱 테스트 및 자동화 |
| **트리거** | 프론트엔드 기능 검증, UI 디버깅, 스크린샷, 브라우저 로그 |
| **기술** | Playwright (Python) |
| **스크립트** | `scripts/with_server.py` - 서버 라이프사이클 관리 |

---

## 5. 커뮤니케이션 (Communication)

### 5.1 doc-coauthoring
| 항목 | 내용 |
|------|------|
| **이름** | doc-coauthoring |
| **용도** | 문서 공동 작성 워크플로우 |
| **트리거** | 문서 작성, 제안서, 기술 스펙, 의사결정 문서 |
| **단계** | 1) 컨텍스트 수집 → 2) 정제 & 구조화 → 3) 독자 테스트 |

### 5.2 internal-comms
| 항목 | 내용 |
|------|------|
| **이름** | internal-comms |
| **용도** | 내부 커뮤니케이션 작성 |
| **트리거** | 상태 보고서, 리더십 업데이트, 뉴스레터, FAQ, 인시던트 보고 |
| **템플릿** | 3P 업데이트, 회사 뉴스레터, FAQ 답변, 일반 커뮤니케이션 |

---

## Skill 요약 테이블

| # | Skill | 카테고리 | 주요 트리거 키워드 |
|---|-------|----------|-------------------|
| 1 | docx | 문서 | Word, 문서 편집, 추적 변경 |
| 2 | pdf | 문서 | PDF, 폼 작성, 병합, 텍스트 추출 |
| 3 | pptx | 문서 | PowerPoint, 프레젠테이션, 슬라이드 |
| 4 | xlsx | 문서 | Excel, 스프레드시트, 수식, 차트 |
| 5 | frontend-design | 디자인 | 웹 UI, React, HTML/CSS, 대시보드 |
| 6 | canvas-design | 디자인 | 포스터, 아트, PNG, PDF 디자인 |
| 7 | algorithmic-art | 디자인 | 제너레이티브 아트, p5.js, 파티클 |
| 8 | brand-guidelines | 디자인 | 브랜드 컬러, Anthropic 스타일 |
| 9 | theme-factory | 디자인 | 테마, 스타일링, 색상 팔레트 |
| 10 | slack-gif-creator | 디자인 | Slack GIF, 애니메이션 |
| 11 | create-skill | 개발 | skill 생성, SKILL.md |
| 12 | skill-creator | 개발 | skill 가이드, 모듈화 |
| 13 | create-rule | 개발 | Cursor 규칙, 코딩 표준 |
| 14 | create-subagent | 개발 | 서브에이전트, 커스텀 에이전트 |
| 15 | migrate-to-skills | 개발 | 규칙→skill 변환, 마이그레이션 |
| 16 | mcp-builder | 개발 | MCP 서버, API 통합 |
| 17 | update-cursor-settings | 개발 | Cursor 설정, settings.json |
| 18 | web-artifacts-builder | 개발 | React 아티팩트, shadcn/ui |
| 19 | webapp-testing | 테스트 | Playwright, 웹앱 테스트 |
| 20 | doc-coauthoring | 커뮤니케이션 | 문서 공동 작성, 제안서 |
| 21 | internal-comms | 커뮤니케이션 | 내부 커뮤니케이션, 상태 보고 |

---

## 사용 방법

각 skill은 해당 트리거 키워드를 사용하면 자동으로 활성화됩니다.

**예시:**
- "Word 문서 만들어줘" → `docx` skill 활성화
- "React 대시보드 디자인해줘" → `frontend-design` skill 활성화
- "MCP 서버 만들어줘" → `mcp-builder` skill 활성화

---

*문서 끝*
