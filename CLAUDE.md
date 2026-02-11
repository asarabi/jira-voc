# CLAUDE.md

## 프로젝트 개요
VOC(고객의 소리)를 채팅으로 입력하면 AI가 Jira 템플릿을 매칭하고 티켓을 자동 생성하는 서비스.

## 기술 스택
- Backend: Python FastAPI (`backend/app/`)
- Frontend: React + TypeScript + Vite (`frontend/src/`)
- AI: OpenAI 호환 API (자체 호스팅 open-oss 서버)
- Jira: Jira Cloud REST API v3
- RAG: ChromaDB (`backend/chromadb_data/` - gitignore됨)

## 프로젝트 구조
- `backend/app/main.py` - FastAPI 엔트리포인트
- `backend/app/config.py` - 환경변수 설정 (Pydantic Settings)
- `backend/app/dependencies.py` - 서비스 DI
- `backend/app/routers/` - API 라우터 (chat, jira_tickets, jira_webhooks, rag, templates)
- `backend/app/services/` - 비즈니스 로직
  - `chat_service.py` - 핵심 오케스트레이션 (VOC → 분류 → 추출 → Jira 생성)
  - `ai_service.py` - LLM 클라이언트 (RAG 컨텍스트 통합)
  - `rag_service.py` - ChromaDB 벡터 검색
  - `jira_service.py` - Jira REST API + ADF 변환
  - `template_service.py` - YAML 템플릿 로더
  - `session_store.py` - 인메모리 채팅 세션
- `backend/app/prompts/` - AI 프롬프트 (분류, 추출, 분석)
- `backend/app/schemas/` - Pydantic 모델
- `backend/templates/` - Jira 이슈 YAML 템플릿
- `frontend/src/components/` - React 컴포넌트 (ChatWindow, MessageBubble 등)
- `frontend/src/hooks/useChat.ts` - 채팅 상태 관리

## 개발 명령어
```bash
# 백엔드 실행
cd backend && uvicorn app.main:app --reload

# 프론트엔드 실행
cd frontend && npm run dev

# 프론트엔드 빌드
cd frontend && npm run build

# 프론트엔드 타입 체크
cd frontend && npx tsc --noEmit
```

## 설정
- 환경변수: `backend/.env` (`.env.example` 참조)
- AI 서버: `AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL_NAME`
- Jira: `JIRA_BASE_URL`, `JIRA_USER_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`

## 핵심 흐름
1. 사용자 VOC 입력 → `POST /api/chat`
2. `chat_service` → `ai_service.classify_voc()` (RAG 컨텍스트 포함)
3. 템플릿 매칭 → `ai_service.extract_fields()` → 미리보기 반환
4. 사용자 확인 → `POST /api/chat/{id}/confirm` → `jira_service.create_issue()`
5. Jira Webhook → `ai_service.analyze_ticket()` (RAG 참조) → Jira 코멘트

## 코딩 규칙
- 백엔드: Python 3.10+, 타입 힌트 사용, async/await
- 프론트엔드: TypeScript strict, 함수형 컴포넌트
- Jira 템플릿: YAML 파일로 관리 (`backend/templates/`)
- AI 프롬프트: 한국어 기본, JSON 응답 포맷
