# CLAUDE_ko.md

이 파일은 이 저장소에서 작업할 때 Claude Code (claude.ai/code)에게 가이드를 제공합니다.

## 프로젝트 개요

StockBot은 나스닥 주식의 이동평균선 교차(5일선 vs 60일선)를 감지하고 텔레그램과 이메일로 알림을 보내는 Python 애플리케이션입니다. 시스템은 데이터베이스 백엔드로 Supabase를 사용하고 주식 데이터는 Yahoo Finance에서 가져옵니다.

## 아키텍처

코드베이스는 명확한 관심사 분리를 통한 모듈식 아키텍처를 따릅니다:

- `main.py` - 두 가지 주요 명령어가 있는 CLI 인터페이스: `ingest` (데이터 수집), `signals` (교차 감지)
- `stockbot/` - 다음을 포함하는 주요 애플리케이션 모듈:
  - `config.py` - 환경 설정 관리
  - `db.py` - Supabase 데이터베이스 작업
  - `yf_client.py` - Yahoo Finance API 클라이언트
  - `ingest.py` - 주식 데이터 수집 로직
  - `indicators.py` - 이동평균 계산 및 교차 감지
  - `signals.py` - 신호 감지 오케스트레이션 및 알림 전송
  - `notifiers.py` - 텔레그램 및 이메일 알림 핸들러
- `tests/` - pytest를 사용한 단위 테스트
- `scripts/` - Supabase 연결 테스트를 포함한 유틸리티 스크립트

## 개발 명령어

### 설치
```bash
# pip 사용
pip install -r requirements.txt

# uv 사용 (권장)
uv sync
```

### 테스트
```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 테스트 실행
pytest --cov=stockbot

# 특정 테스트 마커 실행
pytest -m "not slow"
pytest -m integration
pytest -m unit
```

### 애플리케이션 명령어
```bash
# 주식 데이터 수집
python main.py ingest --tickers AAPL,GOOGL,MSFT

# 신호 감지 실행 (테스트용 dry-run)
python main.py signals --dry-run

# 디버그 모드로 신호 감지 실행 (교차 신호 강제 생성)
python main.py signals --debug

# 특정 티커에 대해 신호 감지 실행
python main.py signals --tickers AAPL,GOOGL
```

### 데이터베이스 테스트
```bash
# Supabase 연결 테스트
python scripts/supabase_smoke_test.py

# 데이터베이스 스키마 적용
python scripts/supabase_smoke_test.py --apply-schema

# 익명 키로 테스트
python scripts/supabase_smoke_test.py --use-anon

# 테스트 데이터 정리
python scripts/supabase_smoke_test.py --cleanup
```

## 주요 설정

환경 변수는 `config.py`에서 관리되며 `.env`에 설정해야 합니다:

### 필수 설정
- `SUPABASE_URL` - Supabase 프로젝트 URL
- `SUPABASE_SERVICE_ROLE_KEY` 또는 `SUPABASE_ANON_KEY` - 데이터베이스 접근 키

### 선택 설정
- `TICKERS` - 기본 주식 심볼 목록 (쉼표로 구분)
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` - 텔레그램 알림용
- SMTP 설정 (`SMTP_HOST`, `SMTP_PORT` 등) - 이메일 알림용

## 데이터 흐름

1. **수집**: `main.py ingest` → `yf_client.py` → Yahoo Finance API → `db.py` → Supabase
2. **신호 감지**: `main.py signals` → `db.py` (데이터 조회) → `indicators.py` (교차 계산) → `notifiers.py` (알림 전송)

시스템은 이동평균을 계산하고 교차를 감지하기 위해 최소 60일의 과거 데이터가 필요합니다.

## 테스트 전략

- 단위 테스트는 포괄적인 교차 감지 시나리오를 통해 `indicators.py` 모듈에 집중
- 데이터베이스 작업을 위한 통합 테스트 사용 가능
- 테스트 마커: `unit`, `integration`, `slow`
- 픽스처는 재현 가능한 테스트를 위한 샘플 OHLC 데이터 제공

## 개발 노트

- 전체적으로 타입 힌트가 있는 Python 3.12+ 사용
- 설정 및 데이터 모델을 위한 데이터클래스
- Async/await 패턴 미사용 - 동기 작업만 사용
- 오류 처리는 우아한 성능 저하에 집중 (누락된 알림이 수집을 중단시키지 않음)
- 실제 교차를 기다리지 않고 신호 감지를 테스트할 수 있는 디버그 모드 사용 가능