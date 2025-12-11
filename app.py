import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# --- 페이지 설정 ---
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
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 로딩 함수 ---
@st.cache_data(ttl=300)
def get_data():
    tickers = ["TQQQ", "QQQ", "KRW=X"]
    data = yf.download(tickers, period="2y", interval="1wk", progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        df = data['Close']
    else:
        df = data
    return df

# --- RSI 계산 ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def main():
    st.title("🔥 PROJECT GLOBAL FIRE: Command Center")
    st.markdown(f"**Ver 9.2 Protocol** | Date: {datetime.now().strftime('%Y-%m-%d')}")

    with st.spinner('🛰️ 위성 데이터 수신 중...'):
        df = get_data()

    if df is not None:
        # --- 데이터 가공 ---
        # 1. TQQQ (Main Asset)
        tqqq_now = df['TQQQ'].iloc[-1]
        tqqq_prev = df['TQQQ'].iloc[-2]
        tqqq_chg = ((tqqq_now - tqqq_prev) / tqqq_prev) * 100
        
        tqqq_high = df['TQQQ'].tail(52).max()
        tqqq_mdd = ((tqqq_now - tqqq_high) / tqqq_high) * 100
        
        rsi_series = calculate_rsi(df['TQQQ'])
        rsi_now = rsi_series.iloc[-1]

        # 2. QQQ (Benchmark) - 추가됨
        qqq_now = df['QQQ'].iloc[-1]
        qqq_high = df['QQQ'].tail(52).max()
        qqq_mdd = ((qqq_now - qqq_high) / qqq_high) * 100

        # 3. 환율
        usd_krw = df['KRW=X'].iloc[-1]

        # --- 대시보드 UI ---
        
        # [ROW 1] 핵심 센서
        st.subheader("1. Main Sensors (TQQQ)")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("TQQQ Price", f"${tqqq_now:.2f}", f"{tqqq_chg:.2f}%")
        with c2: st.metric("USD/KRW", f"₩{usd_krw:.0f}")
        with c3: 
            rsi_label = "NORMAL"
            if rsi_now >= 80: rsi_label = "MADNESS"
            elif rsi_now >= 75: rsi_label = "WARNING"
            st.metric("Weekly RSI (14)", f"{rsi_now:.1f}", rsi_label, delta_color="inverse")
        with c4:
            mdd_label = "STABLE"
            if tqqq_mdd <= -50: mdd_label = "TOTAL WAR"
            elif tqqq_mdd <= -20: mdd_label = "CRISIS"
            st.metric("TQQQ MDD", f"{tqqq_mdd:.2f}%", mdd_label)

        # [ROW 2] 시장 상황 (QQQ Cross-Check) - 신규 추가
        st.subheader("2. Market Context (QQQ Benchmark)")
        qc1, qc2 = st.columns(2)
        with qc1:
            st.metric("QQQ Price (Nasdaq 100)", f"${qqq_now:.2f}")
        with qc2:
            # QQQ MDD 색상 로직
            q_mdd_label = "STABLE"
            if qqq_mdd <= -20: q_mdd_label = "BEAR MARKET"
            elif qqq_mdd <= -10: q_mdd_label = "CORRECTION"
            st.metric("QQQ MDD (Real Market)", f"{qqq_mdd:.2f}%", q_mdd_label)
        
        st.info(f"💡 **Insight:** 현재 시장(QQQ)은 고점 대비 **{qqq_mdd:.2f}%** 위치이며, 레버리지(TQQQ)는 **{tqqq_mdd:.2f}%** 위치입니다.")

        st.divider()

        # [ROW 3] CRO Action Protocol
        st.subheader("3. CRO Action Protocol")
        
        final_action = ""
        bg_color = ""
        
        # 로직은 TQQQ 기준 (가장 민감한 자산 기준)
        if rsi_now >= 80:
            bg_color = "red"
            final_action = "🚨 [MADNESS] 강력 매도 경보\n\n- TQQQ 매수 절대 금지\n- 현금 비중 +10%p 추가 확보\n- 보고 요망."
        elif rsi_now >= 75:
            bg_color = "orange"
            final_action = "⚠️ [WARNING] 과열 경보\n\n- TQQQ 매수 금지\n- 목표 현금 비중 리밸런싱\n- 보고 요망."
        elif tqqq_mdd <= -50: # TQQQ -50%는 QQQ -20% 수준의 위기
            bg_color = "green"
            final_action = "⚔️ [TOTAL WAR] 전면전 선포\n\n- 현금 100% 투입 (All-In)\n- 인생 역전 구간."
        elif tqqq_mdd <= -30:
            bg_color = "blue"
            final_action = "🛡️ [CRISIS LV2] 공포 구간\n\n- 현금 30% 투입\n- 기계적 매수."
        elif tqqq_mdd <= -20:
            bg_color = "blue"
            final_action = "🛡️ [CRISIS LV1] 조정 구간\n\n- 현금 20% 투입\n- 1차 방어선."
        else:
            bg_color = "gray"
            final_action = "✅ [NORMAL] 평시 운용\n\n- 월 적립금 투입 (무지성 적립)\n- 정기 리밸런싱 수행\n- 특이사항 없음."

        if bg_color == "red": st.error(final_action)
        elif bg_color == "orange": st.warning(final_action)
        elif bg_color == "green": st.success(final_action)
        elif bg_color == "blue": st.info(final_action)
        else: st.info(final_action)

if __name__ == "__main__":
    main()
