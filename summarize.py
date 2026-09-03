"""
이미 생성된 data_*.csv 파일들로부터
종목별 요약 통계(기간수익률, 평균변동성, 최대하락일)만 다시 출력한다.
(데이터를 다시 받을 필요 없이, main.py에서 저장해둔 CSV만 읽는다)
"""

import pandas as pd

STOCKS = [
    "삼성전자", "SK하이닉스", "현대차", "기아", "카카오",
    "NAVER", "LG화학", "삼성SDI", "SK이노베이션", "고려아연",
]


def summarize_csv(names: list) -> None:
    for name in names:
        df = pd.read_csv(f"data_{name}.csv", index_col=0, parse_dates=True)

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
    summarize_csv(STOCKS)
