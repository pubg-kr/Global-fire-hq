import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 페이지 설정 (모바일 친화적) ---
st.set_page_config(page_title="Global Fire HQ", page_icon="🔥", layout="wide")

# --- 스타일 커스텀 ---
st.markdown("""
    <style>
    .metric-container {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        text-align: center;
    }
    .big-text { font-size: 20px; font-weight: bold; color: #ffffff; }
    .sub-text { font-size: 14px; color: #aaaaaa; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 로딩 함수 ---
@st.cache_data(ttl=300)
def get_data():
    # TQQQ, QQQ, 환율(KRW=X) 동시 호출
    tickers = ["TQQQ", "QQQ", "KRW=X"]
    data = yf.download(tickers, period="2y", interval="1wk", progress=False)
    
    # 컬럼 레벨 정리 (MultiIndex 해제)
    if isinstance(data.columns, pd.MultiIndex):
        df = data['Close']
    else:
        df = data
        
    return df

# --- RSI 계산 (주봉 14) ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def main():
    st.title("🔥 PROJECT GLOBAL FIRE: Command Center")
    st.markdown(f"**Ver 9.1 Protocol** | Date: {datetime.now().strftime('%Y-%m-%d')}")

    with st.spinner('🛰️ 위성 데이터 수신 중... (Market Data)'):
        df = get_data()

    if df is not None:
        # 1. 데이터 추출 및 가공
        # TQQQ
        tqqq_now = df['TQQQ'].iloc[-1]
        tqqq_prev = df['TQQQ'].iloc[-2]
        tqqq_chg = ((tqqq_now - tqqq_prev) / tqqq_prev) * 100
        
        # MDD (최근 52주 고점 대비)
        tqqq_52w = df['TQQQ'].tail(52)
        tqqq_high = tqqq_52w.max()
        mdd = ((tqqq_now - tqqq_high) / tqqq_high) * 100
        
        # RSI (주봉)
        rsi_series = calculate_rsi(df['TQQQ'])
        rsi_now = rsi_series.iloc[-1]

        # 환율
        usd_krw = df['KRW=X'].iloc[-1]

        # 2. 대시보드 UI 구성
        
        # [ROW 1] 시장 데이터 (Market Data)
        st.subheader("1. Market Sensors")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric("TQQQ Price", f"${tqqq_now:.2f}", f"{tqqq_chg:.2f}%")
        with c2:
            st.metric("USD/KRW (환율)", f"₩{usd_krw:.0f}")
        with c3:
            # RSI 상태 표시
            rsi_label = "NORMAL"
            if rsi_now >= 80: rsi_label = "MADNESS"
            elif rsi_now >= 75: rsi_label = "WARNING"
            st.metric("Weekly RSI (14)", f"{rsi_now:.1f}", rsi_label, delta_color="inverse")
        with c4:
            # MDD 상태 표시
            mdd_label = "STABLE"
            if mdd <= -50: mdd_label = "TOTAL WAR"
            elif mdd <= -20: mdd_label = "CRISIS"
            st.metric("MDD (Drawdown)", f"{mdd:.2f}%", mdd_label)

        st.divider()

        # [ROW 2] CRO 판단 (Decision Engine)
        st.subheader("2. CRO Action Protocol (Ver 9.1)")
        
        # 로직 엔진
        final_action = ""
        bg_color = ""
        
        if rsi_now >= 80:
            bg_color = "red"
            final_action = "🚨 [MADNESS] 강력 매도 경보\n\n- TQQQ 매수 절대 금지\n- 현금 비중 +10%p 추가 확보 (강제 매도)\n- 즉시 CRO에게 보고하시오."
        elif rsi_now >= 75:
            bg_color = "orange"
            final_action = "⚠️ [WARNING] 과열 경보\n\n- TQQQ 매수 금지\n- 목표 현금 비중(30~50%)까지 리밸런싱 매도 수행\n- CRO에게 보고하시오."
        elif mdd <= -50:
            bg_color = "green"
            final_action = "⚔️ [TOTAL WAR] 전면전 선포\n\n- 보유 현금 100% 투입 (All-In)\n- 인생 역전 구간 진입\n- CRO 승인 후 즉시 집행."
        elif mdd <= -30:
            bg_color = "blue"
            final_action = "🛡️ [CRISIS LV2] 공포 구간\n\n- 보유 현금의 30% 투입\n- 기계적 매수 수행."
        elif mdd <= -20:
            bg_color = "blue"
            final_action = "🛡️ [CRISIS LV1] 조정 구간\n\n- 보유 현금의 20% 투입\n- 1차 방어선 구축."
        else:
            bg_color = "gray"
            final_action = "✅ [NORMAL] 평시 운용\n\n- 월 적립금(500만원+) 투입\n- 정기 리밸런싱(현금비중 맞추기) 수행\n- 특이사항 없음."

        # 결과 출력 박스
        if bg_color == "red":
            st.error(final_action)
        elif bg_color == "orange":
            st.warning(final_action)
        elif bg_color == "green":
            st.success(final_action)
        elif bg_color == "blue":
            st.info(final_action)
        else:
            st.info(final_action)

        st.caption("※ 이 화면을 캡처하여 매월 CRO(Gemini)에게 전송하십시오.")

if __name__ == "__main__":
    main()
