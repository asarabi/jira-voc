# VOC-to-Jira 서비스 구현 계획

## Context
고객의 소리(VOC)를 채팅으로 입력하면 AI가 적절한 Jira 템플릿을 매칭하고, 필드를 자동 채워 Jira 티켓을 생성하며, 생성된 티켓에 대해 AI가 분석/답변을 제공하는 서비스.

**Tech Stack**: React + FastAPI + OpenAI 호환 API (open-oss) + Jira Cloud REST API + ChromaDB (RAG)

## 아키텍처

```
┌─────────────────────────────────────────────────────┐
│  React 프론트엔드 (채팅 UI)                           │
│  - 사용자 VOC 입력                                    │
│  - 템플릿 미리보기/수정                                │
│  - 티켓 생성 확인                                     │
└──────────────┬──────────────────────────────────────┘
               │ /api/chat, /api/chat/{id}/confirm
               ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI 백엔드                                      │
│                                                     │
│  1. 사용자 메시지 수신                                 │
│  2. ChromaDB 검색 (RAG) ──→ 유사 VOC + 가이드 참조    │
│  3. YAML 템플릿 매칭                                  │
│  4. 검색결과 + VOC + 템플릿 조합                       │
│  5. LLM API 호출 ──────────→ open-oss 서버            │
│  6. 응답에서 Jira 생성 ────→ Jira Cloud REST API      │
│  7. 결과 반환                                        │
└─────────────────────────────────────────────────────┘
```

## 핵심 워크플로우

### 1. VOC → Jira 생성
```
사용자 VOC 입력
  → ChromaDB에서 유사 과거 VOC + 관련 가이드 검색
  → AI 템플릿 분류 (confidence 기반)
    → 높은 확신: 필드 추출 → 미리보기 → 사용자 확인 → Jira 생성
    → 낮은 확신: 추가 질문 → 사용자 답변 → 재분류
```

### 2. Jira 티켓 → AI 응답
```
Jira Webhook (issue_created)
  → 백엔드 수신
  → ChromaDB에서 관련 가이드/사례 검색
  → AI 분석 (참고 자료 기반)
  → Jira 코멘트 등록
```

## AI 프롬프트 전략 (2단계 분리)
- **1단계 (분류)**: VOC + 템플릿 요약 + RAG 컨텍스트 → 매칭 (JSON: template_id, confidence)
- **2단계 (추출)**: VOC + 매칭된 템플릿 필드 정의 → 필드값 추출 (JSON)
- **분석**: 티켓 정보 + RAG 참고 자료 → 근본 원인 분석 + 해결 방안

## RAG (ChromaDB)
- **past_vocs 컬렉션**: 과거 VOC 데이터 저장. 새 VOC 입력 시 유사 사례 검색
- **guides 컬렉션**: 가이드/매뉴얼 문서 저장. 티켓 분석 시 관련 가이드 참조
- API로 데이터 업로드: `/api/rag/vocs/upload`, `/api/rag/guides/upload`

## 프로젝트 구조

```
jira-voc/
├── .env.example
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── chromadb_data/          # ChromaDB 영구 저장소 (gitignore)
│   ├── app/
│   │   ├── main.py             # FastAPI 엔트리포인트
│   │   ├── config.py           # Pydantic Settings
│   │   ├── dependencies.py     # DI 설정
│   │   ├── routers/
│   │   │   ├── chat.py         # 채팅 API
│   │   │   ├── jira_tickets.py # Jira 티켓 API
│   │   │   ├── jira_webhooks.py# Jira 웹훅
│   │   │   ├── rag.py          # RAG 데이터 관리 API
│   │   │   └── templates.py    # 템플릿 조회 API
│   │   ├── schemas/            # Pydantic 모델
│   │   ├── services/
│   │   │   ├── ai_service.py   # AI 클라이언트 (RAG 통합)
│   │   │   ├── chat_service.py # 오케스트레이션
│   │   │   ├── jira_service.py # Jira REST API
│   │   │   ├── rag_service.py  # ChromaDB RAG
│   │   │   ├── session_store.py# 세션 관리
│   │   │   └── template_service.py
│   │   └── prompts/            # AI 프롬프트
│   └── templates/              # Jira YAML 템플릿
└── frontend/
    └── src/
        ├── components/         # ChatWindow, MessageBubble, TemplatePreview 등
        ├── hooks/useChat.ts
        ├── api/client.ts
        └── types/index.ts
```

## API 엔드포인트

| 엔드포인트 | 설명 |
|---|---|
| `GET /health` | 헬스체크 |
| `POST /api/chat` | VOC 메시지 전송 → AI 분류/추출 |
| `GET /api/chat/{id}/history` | 채팅 이력 조회 |
| `POST /api/chat/{id}/confirm` | 템플릿 확인 → Jira 생성 |
| `GET /api/templates` | 템플릿 목록 |
| `GET /api/templates/{id}` | 템플릿 상세 |
| `POST /api/jira/create` | Jira 직접 생성 |
| `GET /api/jira/ticket/{key}` | Jira 티켓 조회 |
| `POST /api/webhooks/jira` | Jira 웹훅 수신 |
| `GET /api/rag/stats` | RAG 데이터 통계 |
| `POST /api/rag/vocs/upload` | VOC 데이터 파일 업로드 |
| `POST /api/rag/guides/upload` | 가이드 파일 업로드 |
| `POST /api/rag/vocs/search` | VOC 유사 검색 |
| `POST /api/rag/guides/search` | 가이드 유사 검색 |

## 주요 설정값 (.env)
```
AI_BASE_URL=http://your-oss-server:8000/v1
AI_API_KEY=roo-code-key
AI_MODEL_NAME=your-model-name
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_USER_EMAIL=bot@yourorg.com
JIRA_API_TOKEN=jira-api-token
JIRA_PROJECT_KEY=VOC
```

## 주요 의존성
- **Backend**: fastapi, uvicorn, httpx, openai, pyyaml, pydantic-settings, chromadb
- **Frontend**: react, react-dom, vite, typescript
