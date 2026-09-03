"""
M1-1 보너스 과제: 시계열 심화 옵션 (B) 간단 예측
- '베이스라인' 방식으로 짧은 구간(10 거래일)을 예측해보고,
  정확도 자체보다 "이 방식이 가진 가정과 한계"를 보여주는 데 목적이 있다.
- 대상 종목: 삼성전자 (data_삼성전자.csv 사용 — 먼저 main.py를 실행해서 만들어둬야 한다)
"""

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = ["AppleGothic", "NanumGothic", "Malgun Gothic", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

STOCK_NAME = "삼성전자"
HOLDOUT_DAYS = 10  # 마지막 10거래일을 '미래'라고 가정하고 떼어낸다


def load_close_series(name: str) -> pd.Series:
    df = pd.read_csv(f"data_{name}.csv", index_col=0, parse_dates=True)
    return df["Close"]


def naive_forecast(train: pd.Series, horizon: int) -> pd.Series:
    """
    [베이스라인 1] Naive(지속성) 예측
    가정: "내일도 오늘과 같을 것이다" — 가장 단순한 가정으로,
    마지막 관측값을 예측 기간 내내 그대로 반복한다.
    """
    last_value = train.iloc[-1]
    return pd.Series([last_value] * horizon)


def drift_forecast(train: pd.Series, horizon: int) -> pd.Series:
    """
    [베이스라인 2] Drift(추세 연장) 예측
    가정: "최근까지의 평균적인 하루 변화폭이 앞으로도 계속될 것이다"
    (마지막 값 + 최근 평균 일간 변화량 * n일)
    """
    daily_change = train.diff().mean()  # 최근까지의 평균 일간 변화량
    last_value = train.iloc[-1]
    return pd.Series([last_value + daily_change * (i + 1) for i in range(horizon)])


def evaluate(actual: pd.Series, predicted: pd.Series) -> float:
    """평균절대오차(MAE, 원 단위) — 참고용 수치일 뿐, 이 예측의 '정확성'을 보증하지 않는다."""
    return (actual.values - predicted.values).__abs__().mean()


if __name__ == "__main__":
    close = load_close_series(STOCK_NAME)

    train = close.iloc[:-HOLDOUT_DAYS]   # 마지막 10일을 제외한 나머지 = 학습 구간
    actual = close.iloc[-HOLDOUT_DAYS:]  # 실제로 일어난 마지막 10일 = 정답(비교용)

    naive_pred = naive_forecast(train, HOLDOUT_DAYS)
    drift_pred = drift_forecast(train, HOLDOUT_DAYS)

    naive_mae = evaluate(actual, naive_pred)
    drift_mae = evaluate(actual, drift_pred)

    print(f"[{STOCK_NAME}] 최근 {HOLDOUT_DAYS}거래일 예측 결과")
    print(f"Naive(지속성) 예측 MAE: {naive_mae:,.0f}원")
    print(f"Drift(추세연장) 예측 MAE: {drift_mae:,.0f}원")

    # -----------------------------
    # 시각화: 실제값 vs 두 베이스라인 예측
    # -----------------------------
    fig, ax = plt.subplots(figsize=(10, 5))

    # 맥락을 보여주기 위해 학습 구간 마지막 30일도 함께 그린다
    context = train.iloc[-30:]
    ax.plot(context.index, context.values, label="실제 (학습구간)", color="gray")
    ax.plot(actual.index, actual.values, label="실제 (검증구간, 정답)", color="black", linewidth=2)
    ax.plot(actual.index, naive_pred.values, label="Naive 예측", linestyle="--", color="tab:blue")
    ax.plot(actual.index, drift_pred.values, label="Drift 예측", linestyle="--", color="tab:orange")

    ax.axvline(train.index[-1], color="red", linestyle=":", linewidth=1)  # 예측 시작 시점 표시
    ax.set_title(f"{STOCK_NAME}: 베이스라인 방식 {HOLDOUT_DAYS}거래일 예측")
    ax.set_ylabel("종가(원)")
    ax.legend()
    fig.tight_layout()
    fig.savefig("chart4_forecast_baseline.png", dpi=150)
    print("[저장완료] chart4_forecast_baseline.png")
