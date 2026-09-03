"""
M1-1 과제: 국내 대형주 20종목 시계열 분석
- 업종 다양화: 반도체/자동차/플랫폼/2차전지/바이오/금융/에너지/철강 등
- requirements.txt에 넣을 패키지: yfinance, pandas, matplotlib
"""

import pandas as pd
import yfinance as yf

# -----------------------------
# 1. 분석 대상 종목 정의 (업종을 골고루 섞어 20종목)
# -----------------------------
TICKERS = {
    "005930.KS": "삼성전자",       # 반도체
    "000660.KS": "SK하이닉스",     # 반도체
    "005380.KS": "현대차",         # 자동차
    "000270.KS": "기아",           # 자동차
    "035720.KS": "카카오",         # 플랫폼
    "035420.KS": "NAVER",          # 플랫폼
    "051910.KS": "LG화학",         # 화학/배터리소재
    "006400.KS": "삼성SDI",        # 2차전지
    "096770.KS": "SK이노베이션",   # 에너지/배터리
    "010130.KS": "고려아연",       # 비철금속
    # "068270.KS": "셀트리온",       # 바이오
    # "207940.KS": "삼성바이오로직스", # 바이오
    # "105560.KS": "KB금융",         # 금융
    # "055550.KS": "신한지주",       # 금융
    # "086790.KS": "하나금융지주",   # 금융
    # "032830.KS": "삼성생명",       # 보험
    # "015760.KS": "한국전력",       # 에너지(공기업)
    # "012330.KS": "현대모비스",     # 자동차부품
    # "003670.KS": "포스코퓨처엠",   # 2차전지소재
    # "018260.KS": "삼성에스디에스", # IT서비스
}

# 최소 100개 데이터 포인트 요구사항 충족을 위해 1년치(영업일 기준 약 240개) 수집
PERIOD = "1y"
INTERVAL = "1d"


def fetch_data(tickers: dict) -> dict:
    """
    종목별로 Yahoo Finance에서 일별 시세를 받아온다.
    반환값: {종목명: DataFrame} 형태의 딕셔너리
    """
    data = {}
    for code, name in tickers.items():
        df = yf.download(code, period=PERIOD, interval=INTERVAL, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        data[name] = df
        print(f"[수집완료] {name}({code}): {len(df)}개 포인트, "
              f"기간 {df.index.min().date()} ~ {df.index.max().date()}")
    return data


def clean_data(data: dict) -> dict:
    """
    결측치를 확인하고, 있다면 선형보간(interpolate)으로 채운다.
    """
    cleaned = {}
    for name, df in data.items():
        missing_count = df["Close"].isna().sum()
        if missing_count > 0:
            print(f"[정제] {name}: 결측치 {missing_count}개 발견 -> 선형보간으로 처리")
            df["Close"] = df["Close"].interpolate(method="linear")
        else:
            print(f"[정제] {name}: 결측치 없음")
        cleaned[name] = df
    return cleaned


def analyze(data: dict, window: int = 20) -> dict:
    """
    시계열 분석 기법 2가지를 적용한다.
    1) 이동평균(rolling mean): 최근 N일 평균으로 잔물결(노이즈)을 지우고 큰 흐름(추세)만 본다.
    2) 일간 변화율(pct_change): 어제 대비 오늘 종가가 몇 % 움직였는지를 계산해 변동성을 본다.
    """
    for name, df in data.items():
        df["MA_20"] = df["Close"].rolling(window=window).mean()
        df["Daily_Return_%"] = df["Close"].pct_change() * 100
        df["Volatility_20"] = df["Daily_Return_%"].rolling(window=window).std()
        data[name] = df
    return data


def summarize(data: dict) -> None:
    """
    종목별 핵심 수치를 콘솔에 요약 출력한다.
    """
    for name, df in data.items():
        start_price = df["Close"].iloc[0]
        end_price = df["Close"].iloc[-1]
        total_return = (end_price - start_price) / start_price * 100
        avg_volatility = df["Volatility_20"].mean()
        max_drop_day = df["Daily_Return_%"].idxmin()
        max_drop_val = df["Daily_Return_%"].min()

        print(f"\n--- {name} 요약 ---")
        print(f"기간 수익률: {total_return:.2f}%")
        print(f"평균 20일 변동성: {avg_volatility:.2f}")
        print(f"최대 하락일: {max_drop_day.date()} ({max_drop_val:.2f}%)")


if __name__ == "__main__":
    raw = fetch_data(TICKERS)
    cleaned = clean_data(raw)
    analyzed = analyze(cleaned)
    summarize(analyzed)

    for name, df in analyzed.items():
        filename = f"data_{name}.csv"
        df.to_csv(filename, encoding="utf-8-sig")
        print(f"[저장완료] {filename}")