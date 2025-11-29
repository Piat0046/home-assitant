# Home AI - 음성 인식 홈 IoT 어시스턴트

음성 인식으로 동작하는 스마트 홈 IoT 어시스턴트입니다. 음성 명령을 통해 조명, 알람, 온도 조절기 등의 IoT 디바이스를 제어할 수 있습니다.

## 주요 기능

- **음성 인식 (STT)**: Google Speech Recognition 또는 OpenAI Whisper API
- **음성 합성 (TTS)**: gTTS 또는 OpenAI TTS API
- **LLM 통합**: OpenAI GPT 또는 Claude를 통한 자연어 이해
- **IoT 제어**: MCP(Model Context Protocol) 기반 디바이스 제어
- **클라이언트-서버 분리**: REST API 및 WebSocket 지원

## 아키텍처

```
[클라이언트] → [STT] → [서버 API] → [LLM] → [MCP IoT] → [TTS] → [클라이언트]
```

## 지원 디바이스 (시뮬레이션)

- **조명**: 거실, 침실, 주방 조명 켜기/끄기/밝기 조절
- **알람**: 알람 설정/취소/목록 조회
- **온도 조절기**: 온도 설정/모드 변경

## 설치

### uv 사용 (권장)

```bash
# 프로젝트 클론
git clone git@github.com:Piat0046/home-assitant.git
cd home-assitant

# 의존성 설치
uv sync --extra dev

# 환경 변수 설정
cp env.example .env
# .env 파일 편집하여 API 키 설정
```

### Docker Compose 사용

```bash
# 환경 변수 설정
cp env.example .env
# .env 파일 편집

# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 환경 변수

```bash
# API 키
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# 데이터베이스
DATABASE_URL=postgresql://home_ai:password@localhost:5432/home_ai
DB_PASSWORD=your-secure-password

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 프로바이더 설정
STT_PROVIDER=google    # google 또는 openai
TTS_PROVIDER=gtts      # gtts 또는 openai
LLM_PROVIDER=openai    # openai 또는 claude
```

## 실행

### 서버 실행

```bash
# MCP IoT 서버 시작
uv run python -m home_ai.mcp_iot.server &

# API 서버 시작
uv run python -m home_ai.server.app
```

### 클라이언트 실행

```bash
# 인터랙티브 클라이언트
uv run python -m home_ai.client.assistant
```

## API 엔드포인트

### REST API

- `GET /health` - 서버 상태 확인
- `POST /api/chat` - 채팅 (텍스트/오디오)
- `GET /api/devices` - 디바이스 상태 조회
- `POST /api/devices/light` - 조명 제어
- `POST /api/devices/alarm` - 알람 제어
- `POST /api/devices/thermostat` - 온도 조절기 제어

### WebSocket

- `WS /ws` - 실시간 채팅

## 테스트

```bash
# 전체 테스트 실행
uv run pytest tests/ -v

# 커버리지 포함
uv run pytest --cov=home_ai --cov-report=html

# E2E 테스트만
uv run pytest tests/e2e/ -v -m e2e

# 통합 테스트 제외
uv run pytest tests/ -v --ignore=tests/e2e -m "not integration"
```

## 프로젝트 구조

```
home-ai/
├── src/home_ai/
│   ├── common/           # 공통 모듈
│   │   ├── interfaces/   # Protocol 인터페이스
│   │   ├── stt/          # STT 구현체
│   │   ├── tts/          # TTS 구현체
│   │   ├── models.py     # 데이터 모델
│   │   └── config.py     # 설정 관리
│   ├── logging/          # 로깅 모듈
│   ├── server/           # 서버 모듈
│   │   ├── api/          # REST/WebSocket API
│   │   ├── llm/          # LLM 구현체
│   │   └── db/           # 데이터베이스
│   ├── client/           # 클라이언트 모듈
│   └── mcp_iot/          # MCP IoT 서버
│       └── devices/      # 디바이스 구현체
├── tests/                # 테스트
├── docker-compose.yml    # Docker Compose 설정
└── pyproject.toml        # 프로젝트 설정
```

## 개발 가이드

이 프로젝트는 TDD(Test-Driven Development) 방식으로 개발되었습니다.

1. **RED**: 테스트 먼저 작성 (실패)
2. **GREEN**: 테스트 통과하는 최소 코드 작성
3. **REFACTOR**: 코드 개선 (테스트 유지)

### 의존성 주입

모든 모듈은 Protocol/Interface를 사용하여 의존성을 분리합니다:

```python
from home_ai.common.interfaces import STTInterface

class MySTT:
    def transcribe(self, audio_data: bytes) -> str:
        # 구현
        pass
```

## 라이선스

MIT License

