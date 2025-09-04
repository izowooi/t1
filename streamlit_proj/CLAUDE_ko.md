# 개발 가이드

이 파일은 Streamlit 주식 차트 프로젝트의 한국어 개발 가이드입니다.

## 프로젝트 개요

Supabase에 저장된 주식 데이터를 기반으로 이동평균선(5일/60일) 차트를 보여주는 Streamlit 웹 애플리케이션입니다. 골든크로스와 데드크로스 신호를 시각적으로 표시합니다.

## 개발 명령어

### 애플리케이션 실행
```bash
streamlit run app.py
```

### 의존성 관리
이 프로젝트는 `uv`를 사용하여 패키지를 관리합니다:
```bash
# 의존성 설치
uv install

# 새 패키지 추가
uv add <패키지명>

# 가상환경 활성화
source .venv/bin/activate
```

## 아키텍처

### 주요 구성 요소

- **app.py**: 모든 기능이 포함된 메인 Streamlit 애플리케이션
- **데이터베이스**: Supabase를 백엔드로 사용하며 주요 테이블은 다음과 같습니다:
  - `tickers`: 사용 가능한 주식 티커 목록
  - `ohlc_daily`: 일별 OHLC(시가, 고가, 저가, 종가) 가격 데이터
- **설정**: 환경 변수와 시크릿은 `.streamlit/secrets.toml`에 저장

### 주요 함수

- `get_client()`: 캐시된 Supabase 클라이언트 연결 생성
- `list_tickers()`: 사용 가능한 주식 티커 조회 (5분 캐시)
- `load_ohlc()`: 특정 티커와 날짜 범위의 OHLC 데이터 로드 (5분 캐시)
- `add_sma()`: 5일 및 60일 단순 이동평균 계산
- `find_cross_points()`: 골든크로스(SMA5 > SMA60)와 데드크로스(SMA5 < SMA60) 신호 식별
- `make_chart()`: 가격선, 이동평균, 크로스 신호가 포함된 Plotly 인터랙티브 차트 생성

### 데이터 흐름

1. 사용자가 사이드바에서 티커와 기간 선택
2. 앱이 Supabase에서 OHLC 데이터 조회
3. 이동평균 계산
4. 가격, 이동평균, 크로스 신호가 포함된 Plotly 차트 생성
5. 차트 하단에 최근 데이터 테이블 표시

## 중요 사항

- 앱은 데이터베이스 쿼리에 5분 TTL을 가진 Streamlit 캐싱(`@st.cache_data`) 사용
- Supabase 인증 정보는 `.streamlit/secrets.toml`에 저장 (git 커밋 제외)
- 한국 사용자를 위한 한국어 UI 제공
- 차트는 더 나은 사용자 경험을 위해 통합 호버 모드 사용
- 골든크로스는 위쪽 삼각형, 데드크로스는 아래쪽 삼각형으로 표시

## 데이터 구조

### Supabase 테이블 구조

**tickers 테이블**:
- `ticker`: 주식 티커 심볼 (예: MSFT, AMZN, CPNG)

**ohlc_daily 테이블**:
- `ticker`: 주식 티커 심볼
- `d`: 날짜
- `open`: 시가
- `high`: 고가
- `low`: 저가
- `close`: 종가
- `volume`: 거래량

## 차트 기능

- **가격 차트**: 종가 기준 선 차트
- **이동평균선**: SMA5(5일), SMA60(60일)
- **골든크로스**: SMA5가 SMA60을 상향 돌파하는 지점 (▲)
- **데드크로스**: SMA5가 SMA60을 하향 돌파하는 지점 (▼)
- **인터랙티브**: 줌, 팬, 호버 정보 제공