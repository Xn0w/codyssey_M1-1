"""
M1-1 과제: 시각화 스크립트 (20종목 대응 버전)
main.py 실행 후 생긴 data_*.csv 파일들을 읽어서
그래프 3종을 만들어 PNG로 저장한다.
"""

import math

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# main.py의 TICKERS와 동일한 종목명 리스트를 유지해야 한다.
STOCKS = [
    "삼성전자", "SK하이닉스", "현대차", "기아", "카카오", "NAVER",
    "LG화학", "삼성SDI", "SK이노베이션", "고려아연",
    # "셀트리온", "삼성바이오로직스",
    # "KB금융", "신한지주", "하나금융지주", "삼성생명",
    # "한국전력", "현대모비스", "포스코퓨처엠", "삼성에스디에스",
]


def load_data(names: list) -> dict:
    """저장해둔 CSV를 다시 불러온다."""
    data = {}
    for name in names:
        df = pd.read_csv(f"data_{name}.csv", index_col=0, parse_dates=True)
        data[name] = df
    return data


def plot_price_with_ma(data: dict):
    """
    [그래프 1] 종목별 종가 + 20일 이동평균
    - 종목 수(n)에 맞춰 서브플롯 그리드를 자동으로 계산한다.
      (예: 20종목이면 대략 5행 x 4열 형태로 배치)
    """
    n = len(data)
    ncols = 4
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 3 * nrows))
    axes = axes.flatten()

    for ax, (name, df) in zip(axes, data.items()):
        ax.plot(df.index, df["Close"], label="종가", alpha=0.4, color="gray")
        ax.plot(df.index, df["MA_20"], label="20일 이동평균", color="tab:blue", linewidth=1.5)
        ax.set_title(name, fontsize=10)
        ax.tick_params(axis="x", rotation=30, labelsize=7)
        ax.tick_params(axis="y", labelsize=7)

    # 종목 수가 그리드 칸 수보다 적으면 남는 서브플롯은 숨긴다.
    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle("종목별 종가 추세 (원본 vs 20일 이동평균)", fontsize=14)
    fig.tight_layout()
    fig.savefig("chart1_price_ma.png", dpi=150)
    print("[저장완료] chart1_price_ma.png")
    plt.close(fig)


def plot_volatility(data: dict):
    """
    [그래프 2] 종목별 20일 변동성 비교
    - 종목이 많아 범례가 겹치므로, colormap으로 색을 넉넉히 확보하고
      범례는 그래프 바깥(오른쪽)에 배치한다.
    """
    fig, ax = plt.subplots(figsize=(13, 7))
    colors = plt.cm.tab20.colors  # 최대 20개 구분 가능한 색상표

    for i, (name, df) in enumerate(data.items()):
        ax.plot(df.index, df["Volatility_20"], label=name, color=colors[i % len(colors)])

    ax.set_title("종목별 20일 변동성(표준편차) 비교")
    ax.set_xlabel("날짜")
    ax.set_ylabel("변동성 (%)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, ncol=1)
    fig.tight_layout()
    fig.savefig("chart2_volatility.png", dpi=150, bbox_inches="tight")
    print("[저장완료] chart2_volatility.png")
    plt.close(fig)


def plot_normalized_return(data: dict):
    """
    [그래프 3] 시작일=100 기준 누적 수익률 비교
    """
    fig, ax = plt.subplots(figsize=(13, 7))
    colors = plt.cm.tab20.colors

    for i, (name, df) in enumerate(data.items()):
        normalized = df["Close"] / df["Close"].iloc[0] * 100
        ax.plot(df.index, normalized, label=name, color=colors[i % len(colors)])

    ax.axhline(100, color="gray", linestyle="--", linewidth=1)
    ax.set_title("종목별 누적 수익률 비교 (시작일=100 기준)")
    ax.set_xlabel("날짜")
    ax.set_ylabel("정규화 지수")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, ncol=1)
    fig.tight_layout()
    fig.savefig("chart3_normalized_return.png", dpi=150, bbox_inches="tight")
    print("[저장완료] chart3_normalized_return.png")
    plt.close(fig)


if __name__ == "__main__":
    data = load_data(STOCKS)
    plot_price_with_ma(data)
    plot_volatility(data)
    plot_normalized_return(data)