"""
M1-1 보너스 과제: Streamlit 대시보드
- 종목과 기간을 바꿔가며 탐색할 수 있는 웹 대시보드
- 배포: Streamlit Community Cloud에 이 파일을 메인으로 지정해서 배포한다.
- 실행(로컬 확인용): streamlit run dashboard.py
- 색상 테마는 .streamlit/config.toml 에서 관리한다 (다크 네이비 + 시안 포인트)
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="국내 대형주 시계열 대시보드",
    page_icon="📈",
    layout="wide",  # 화면을 넓게 써서 그래프가 시원하게 보이도록
)

# -----------------------------
# 한글 폰트 설정
# -----------------------------
# 로컬(macOS)에서는 AppleGothic, 배포 서버(Linux, Streamlit Cloud)에서는
# NanumGothic을 쓰도록 순서대로 시도한다. (NanumGothic은 packages.txt로 설치)
plt.rcParams["font.family"] = ["AppleGothic", "NanumGothic", "Malgun Gothic", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# -----------------------------
# 다크 테마 색상 팔레트
# -----------------------------
# config.toml의 배경색과 맞춰서, matplotlib 차트도 같은 톤(짙은 네이비)으로 그린다.
# 이걸 안 맞추면 "화면은 어두운데 그래프만 하얀 사각형"이 되어 붕 뜨게 된다.
BG_COLOR = "#0F172A"      # config.toml의 backgroundColor와 동일
GRID_COLOR = "#334155"
TEXT_COLOR = "#E2E8F0"
ACCENT_COLOR = "#22D3EE"  # 포인트 컬러(시안) — 이동평균, 강조 라인에 사용
LINE_MUTED = "#64748B"    # 원본 종가처럼 배경처럼 흐리게 깔릴 라인
RED_COLOR = "#F87171"     # 변동성/하락 강조용


def style_axes(ax):
    """차트를 다크 테마 톤에 맞춰 일괄적으로 스타일링하는 헬퍼 함수."""
    ax.set_facecolor(BG_COLOR)
    ax.figure.set_facecolor(BG_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(color=GRID_COLOR, alpha=0.4, linewidth=0.5)
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_facecolor(BG_COLOR)
        legend.get_frame().set_edgecolor(GRID_COLOR)
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)


# -----------------------------
# 종목 목록 (main.py와 동일)
# -----------------------------
TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "현대차": "005380.KS",
    "기아": "000270.KS",
    "카카오": "035720.KS",
    "NAVER": "035420.KS",
    "LG화학": "051910.KS",
    "삼성SDI": "006400.KS",
    "SK이노베이션": "096770.KS",
    "고려아연": "010130.KS",
}


@st.cache_data(ttl=3600)  # 한 시간 동안은 같은 요청이면 다시 다운로드하지 않고 캐시 사용
def load_data(code: str, start, end) -> pd.DataFrame:
    """선택한 종목/기간의 데이터를 받아와 이동평균/변화율/변동성까지 계산해서 반환한다."""
    df = yf.download(code, start=start, end=end, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["Close"] = df["Close"].interpolate(method="linear")  # 결측치 처리
    df["MA_20"] = df["Close"].rolling(window=20).mean()
    df["Daily_Return_%"] = df["Close"].pct_change() * 100
    df["Volatility_20"] = df["Daily_Return_%"].rolling(window=20).std()
    return df


# -----------------------------
# 사이드바: 종목 선택 + 기간 선택
# -----------------------------
st.sidebar.title("⚙️ 설정")
selected_name = st.sidebar.selectbox("종목 선택", list(TICKERS.keys()))
selected_code = TICKERS[selected_name]

date_range = st.sidebar.date_input(
    "기간 선택",
    value=(pd.Timestamp.today() - pd.Timedelta(days=365), pd.Timestamp.today()),
)

# 날짜를 두 개 다 선택하기 전까지는 실행하지 않는다 (에러 방지)
if len(date_range) != 2:
    st.warning("시작일과 종료일을 모두 선택해주세요.")
    st.stop()

start_date, end_date = date_range

# -----------------------------
# 데이터 로드
# -----------------------------
df = load_data(selected_code, start_date, end_date)

st.title(f"📈 {selected_name} 시계열 대시보드")
st.caption(f"기간: {start_date} ~ {end_date}  ·  데이터 출처: Yahoo Finance")

if len(df) < 20:
    st.warning("선택한 기간이 너무 짧아 20일 이동평균/변동성을 계산할 수 없습니다. "
               "기간을 더 넓게 선택해주세요.")
    st.stop()

# -----------------------------
# 핵심 지표 요약 (카드 형태)
# -----------------------------
start_price = df["Close"].iloc[0]
end_price = df["Close"].iloc[-1]
total_return = (end_price - start_price) / start_price * 100
avg_volatility = df["Volatility_20"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("기간 수익률", f"{total_return:.2f}%", delta=f"{total_return:.1f}%")
col2.metric("평균 20일 변동성", f"{avg_volatility:.2f}")
col3.metric("데이터 포인트", f"{len(df)}개")

st.divider()

# -----------------------------
# 그래프 1: 종가 + 이동평균
# -----------------------------
st.subheader("종가 & 20일 이동평균")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df.index, df["Close"], label="종가", alpha=0.6, color=LINE_MUTED)
ax1.plot(df.index, df["MA_20"], label="20일 이동평균", color=ACCENT_COLOR, linewidth=2)
ax1.legend()
style_axes(ax1)
st.pyplot(fig1)

# -----------------------------
# 그래프 2: 변동성
# -----------------------------
st.subheader("20일 변동성 (리스크)")
fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(df.index, df["Volatility_20"], color=RED_COLOR, linewidth=1.8)
ax2.set_ylabel("변동성 (%)")
style_axes(ax2)
st.pyplot(fig2)

# -----------------------------
# 원본 데이터 (선택적으로 펼쳐보기)
# -----------------------------
with st.expander("📋 원본 데이터 표로 보기"):
    st.dataframe(df[["Close", "MA_20", "Daily_Return_%", "Volatility_20"]])