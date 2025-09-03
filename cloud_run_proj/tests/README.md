# 🧪 테스트 실행 가이드

## PyCharm에서 테스트 실행하기

### 방법 1: 함수 옆 녹색 실행 버튼 사용
1. `test_indicators.py` 파일 열기
2. 테스트 함수명 옆에 나타나는 녹색 실행 버튼 클릭
3. 원하는 테스트 함수 선택해서 실행

### 방법 2: 전체 테스트 클래스 실행
1. 클래스명(`TestComputeSMACross`) 옆 녹색 실행 버튼 클릭
2. 전체 테스트 클래스 실행

### 방법 3: 터미널에서 실행
```bash
# uv 환경에서 테스트 실행
uv run pytest tests/

# 특정 테스트 파일만 실행
uv run pytest tests/test_indicators.py

# 특정 테스트 함수만 실행
uv run pytest tests/test_indicators.py::TestComputeSMACross::test_debug_mode_golden_cross -v

# verbose 모드로 실행
uv run pytest tests/ -v
```

## 🎯 주요 테스트 케이스

| 테스트 함수 | 설명 |
|-------------|------|
| `test_insufficient_data` | 데이터 부족 시 None 반환 테스트 |
| `test_normal_operation_no_cross` | 일반 작동 (교차 없음) 테스트 |
| `test_debug_mode_golden_cross` | 디버그 모드 골든크로스 강제 생성 |
| `test_debug_mode_dead_cross` | 디버그 모드 데드크로스 강제 생성 |
| `test_cross_result_structure` | CrossResult 객체 구조 검증 |
| `test_dataframe_structure` | DataFrame 구조 및 컬럼 검증 |

## 🔧 디버그 모드 사용법

### 코드에서 디버그 모드 활성화:
```python
# 강제로 교차 신호 생성
result = compute_sma_cross(data, debug_mode=True)
```

### 커맨드라인에서 디버그 모드:
```bash
# 메인 프로그램에서 디버그 모드 실행
python main.py signals --debug

# 특정 티커만 디버그 모드
python main.py signals --tickers AAPL --debug
```

## 📊 테스트 결과 해석

### ✅ 성공 케이스:
```
tests/test_indicators.py::TestComputeSMACross::test_debug_mode_golden_cross PASSED
```

### ❌ 실패 케이스:
```
tests/test_indicators.py::TestComputeSMACross::test_debug_mode_golden_cross FAILED
    assert cross.signal_type == "golden_cross"
```

## 🐛 문제 해결

### Import 에러:
```bash
# uv 환경에서 설치 확인
uv sync
uv run python -c "import stockbot.indicators"
```

### 모듈 경로 에러:
```python
# PYTHONPATH 설정
import sys
sys.path.append('/path/to/project')
```

## 🚀 다음 단계

1. **실제 데이터로 테스트**: `sample_ohlc_data` 대신 실제 주가 데이터 사용
2. **통합 테스트**: 전체 파이프라인 (DB → 신호 감지 → 알림) 테스트
3. **성능 테스트**: 대용량 데이터 처리 성능 측정
4. **에러 케이스**: 네트워크 오류, API 제한 등 예외 상황 테스트
