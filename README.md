# M1-1 — 국내 대형주 10종목 시계열 분석

국내 대형주 10종목(삼성전자, SK하이닉스, 현대차, 기아, 카카오, NAVER, LG화학, 삼성SDI,
SK이노베이션, 고려아연)의 최근 1년간 주가 데이터를 수집·정제·분석·시각화한 프로젝트입니다.

분석 리포트는 [REPORT.md](./REPORT.md)에서 확인할 수 있습니다.

## 데이터 출처

- Yahoo Finance ([yfinance](https://pypi.org/project/yfinance/) 라이브러리 사용)
- 수집 기간: 약 1년 (2025년 9월 ~ 2026년 9월 기준), 일별 종가 기준

## 실행 방법

### 1. 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

> Homebrew Python 환경에서 `externally-managed-environment` 에러가 발생하면
> (venv가 이미 활성화된 상태에서) 아래 명령으로 재시도하세요.
> ```bash
> pip install --break-system-packages -r requirements.txt
> ```

### 3. 데이터 수집 · 정제 · 분석

```bash
python main.py
```

- Yahoo Finance에서 10종목의 일별 시세를 받아온다.
- 결측치를 확인하고 필요 시 선형보간으로 처리한다.
- 20일 이동평균, 일간 변화율, 20일 변동성을 계산한다.
- 종목별로 `data_{종목명}.csv` 파일을 생성한다.

### 4. 시각화

```bash
python visualize.py
```

- `main.py`가 만든 CSV들을 읽어 그래프 3종을 PNG로 저장한다.
  - `chart1_price_ma.png` — 종목별 종가 + 20일 이동평균
  - `chart2_volatility.png` — 종목별 20일 변동성 비교
  - `chart3_normalized_return.png` — 종목별 누적 수익률 비교 (시작일=100 기준)

### (선택) CSV로부터 요약 통계만 다시 보기

데이터를 다시 받지 않고, 이미 저장된 CSV에서 종목별 수익률/변동성/최대하락일만 다시 보고 싶다면:

```bash
python summarize.py
```

## 폴더 구조

```
codyssey_M1-1/
├── main.py                      # 데이터 수집 · 정제 · 분석
├── visualize.py                 # 시각화 (그래프 3종 생성)
├── summarize.py                 # 저장된 CSV로부터 요약 통계 재출력
├── requirements.txt             # 의존성 목록
├── REPORT.md                    # 분석 리포트
├── chart1_price_ma.png
├── chart2_volatility.png
├── chart3_normalized_return.png
└── data_*.csv                   # 종목별 정제·분석된 데이터
```

## 개발 환경

- Python 3.9 (venv)
- macOS

## 라이선스 / 데이터 이용 주의사항

본 프로젝트는 학습 목적의 과제로, Yahoo Finance에서 제공하는 데이터를 비상업적 학습
용도로 사용했습니다. 실제 투자 판단의 근거로 사용하기에는 데이터 범위와 검증 수준이
부족합니다 (자세한 한계점은 REPORT.md 6번 항목 참고).
