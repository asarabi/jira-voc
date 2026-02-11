# VOC-to-Jira

채팅 인터페이스로 VOC(고객의 소리)를 입력하면 AI가 적절한 Jira 템플릿을 매칭하고 티켓을 자동 생성하는 서비스입니다.

## 주요 기능

- **VOC → Jira 자동 생성**: VOC 입력 → AI 템플릿 매칭 → 필드 자동 추출 → 미리보기 → Jira 티켓 생성
- **RAG 기반 참조**: ChromaDB에 저장된 과거 VOC/가이드 문서를 검색하여 AI 응답 품질 향상
- **Jira Webhook 연동**: 티켓 생성 시 AI가 자동으로 분석 코멘트 등록

## 기술 스택

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python FastAPI
- **AI**: OpenAI 호환 API (open-oss 서버)
- **Jira**: Jira Cloud REST API v3
- **RAG**: ChromaDB (벡터 검색)

## 시작하기

### 1. 환경 설정

```bash
cp .env.example backend/.env
```

`backend/.env`를 편집하여 실제 값을 입력합니다:

```env
AI_BASE_URL=http://your-oss-server:8000/v1
AI_API_KEY=your-api-key
AI_MODEL_NAME=your-model-name

JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_USER_EMAIL=bot@yourorg.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_PROJECT_KEY=VOC
```

### 2. 백엔드 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

채팅 UI: http://localhost:5173

### 4. RAG 데이터 업로드 (선택)

과거 VOC 데이터 (줄 단위 텍스트 파일):
```bash
curl -X POST http://localhost:8000/api/rag/vocs/upload \
  -F "file=@past_vocs.txt"
```

가이드 문서 (빈 줄 기준 단락 분리):
```bash
curl -X POST http://localhost:8000/api/rag/guides/upload \
  -F "file=@guide.txt"
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/api/chat` | VOC 메시지 전송 |
| GET | `/api/chat/{id}/history` | 채팅 이력 |
| POST | `/api/chat/{id}/confirm` | 티켓 생성 확인 |
| GET | `/api/templates` | 템플릿 목록 |
| POST | `/api/jira/create` | Jira 직접 생성 |
| POST | `/api/webhooks/jira` | Jira 웹훅 |
| GET | `/api/rag/stats` | RAG 통계 |
| POST | `/api/rag/vocs/upload` | VOC 파일 업로드 |
| POST | `/api/rag/guides/upload` | 가이드 파일 업로드 |

## Jira 템플릿

YAML 파일로 관리됩니다 (`backend/templates/`):

- `bug_report.yaml` - 버그 리포트
- `feature_request.yaml` - 기능 요청
- `service_request.yaml` - 서비스 요청

새 템플릿 추가 시 YAML 파일을 만들고 서버를 재시작하면 자동 인식됩니다.
