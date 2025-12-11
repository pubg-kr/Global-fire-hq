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

# --- 데이터 로딩 함수 (주봉/월봉 분리 호출) ---
@st.cache_data(ttl=300)
def get_data():
    tickers = ["TQQQ", "QQQ", "KRW=X"]
    
    # 1. 주봉 데이터 (단기/중기 추세용)
    data_wk = yf.download(tickers, period="2y", interval="1wk", progress=False)
    
    # 2. 월봉 데이터 (장기 추세용) - RSI 정확도를 위해 5년치 호출
    data_mo = yf.download(tickers, period="5y", interval="1mo", progress=False)
    
    # MultiIndex 처리
    if isinstance(data_wk.columns, pd.MultiIndex):
        df_wk = data_wk['Close']
        df_mo = data_mo['Close']
    else:
        df_wk = data_wk
        df_mo = data_mo
        
    return df_wk, df_mo

# --- RSI 계산 ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def main():
    st.title("🔥 PROJECT GLOBAL FIRE: Command Center")
    st.markdown(f"**Ver 9.4 Dual-Scope** | Date: {datetime.now().strftime('%Y-%m-%d')}")

    with st.spinner('🛰️ 주간 및 월간 위성 데이터 수신 중...'):
        df_wk, df_mo = get_data()

    if df_wk is not None and df_mo is not None:
        # --- 데이터 가공 ---
        
        # 1. TQQQ Data
        tqqq_now = df_wk['TQQQ'].iloc[-1]
        tqqq_prev = df_wk['TQQQ'].iloc[-2]
        tqqq_chg = ((tqqq_now - tqqq_prev) / tqqq_prev) * 100
        
        # MDD (주봉 기준 52주)
        tqqq_high = df_wk['TQQQ'].tail(52).max()
        tqqq_mdd = ((tqqq_now - tqqq_high) / tqqq_high) * 100
        
        # RSI (주봉 & 월봉)
        tqqq_rsi_wk = calculate_rsi(df_wk['TQQQ']).iloc[-1]
        tqqq_rsi_mo = calculate_rsi(df_mo['TQQQ']).iloc[-1]

        # 2. QQQ Data
        qqq_now = df_wk['QQQ'].iloc[-1]
        qqq_high = df_wk['QQQ'].tail(52).max()
        qqq_mdd = ((qqq_now - qqq_high) / qqq_high) * 100
        
        # RSI (주봉 & 월봉)
        qqq_rsi_wk = calculate_rsi(df_wk['QQQ']).iloc[-1]
        qqq_rsi_mo = calculate_rsi(df_mo['QQQ']).iloc[-1]

        # 3. 환율
        usd_krw = df_wk['KRW=X'].iloc[-1]

        # --- 대시보드 UI ---
        
        # [ROW 1] Main Asset (TQQQ)
        st.subheader("1. Main Asset (TQQQ)")
        # 컬럼 5개로 확장 (가격 | 환율 | 주봉RSI | 월봉RSI | MDD)
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1: st.metric("TQQQ Price", f"${tqqq_now:.2f}", f"{tqqq_chg:.2f}%")
        with c2: st.metric("USD/KRW", f"₩{usd_krw:.0f}")
        with c3: 
            # 주봉 RSI
            rsi_label = "NORMAL"
            if tqqq_rsi_wk >= 80: rsi_label = "MADNESS"
            elif tqqq_rsi_wk >= 75: rsi_label = "WARNING"
            st.metric("주봉(W) RSI", f"{tqqq_rsi_wk:.1f}", rsi_label, delta_color="inverse")
        with c4:
            # 월봉 RSI (참고용)
            st.metric("월봉(M) RSI", f"{tqqq_rsi_mo:.1f}", "Long-Term")
        with c5:
            # MDD
            mdd_label = "STABLE"
            if tqqq_mdd <= -50: mdd_label = "TOTAL WAR"
            elif tqqq_mdd <= -20: mdd_label = "CRISIS"
            st.metric("MDD (Drawdown)", f"{tqqq_mdd:.2f}%", mdd_label)

        st.divider()

        # [ROW 2] Market Benchmark (QQQ)
        st.subheader("2. Market Context (QQQ Benchmark)")
        qc1, qc2, qc3, qc4 = st.columns(4)
        
        with qc1: st.metric("QQQ Price", f"${qqq_now:.2f}")
        with qc2:
            # QQQ 주봉 RSI
            q_rsi_label = "NORMAL"
            if qqq_rsi_wk >= 75: q_rsi_label = "OVERBOUGHT"
            st.metric("QQQ 주봉(W) RSI", f"{qqq_rsi_wk:.1f}", q_rsi_label, delta_color="inverse")
        with qc3:
            # QQQ 월봉 RSI
            st.metric("QQQ 월봉(M) RSI", f"{qqq_rsi_mo:.1f}", "Long-Term")
        with qc4:
            # QQQ MDD
            q_mdd_label = "STABLE"
            if qqq_mdd <= -20: q_mdd_label = "BEAR MARKET"
            st.metric("QQQ MDD", f"{qqq_mdd:.2f}%", q_mdd_label)
        
        # 인사이트
        st.info(f"💡 **Trend Insight:** 현재 TQQQ의 주봉 에너지는 **{tqqq_rsi_wk:.1f}**이며, 장기 추세인 월봉 에너지는 **{tqqq_rsi_mo:.1f}**입니다.")

        st.divider()

        # [ROW 3] CRO Action Protocol
        st.subheader("3. CRO Action Protocol")
        
        final_action = ""
        bg_color = ""
        
        # 로직 (주봉 기준이 메인, 월봉은 참고)
        if tqqq_rsi_wk >= 80:
            bg_color = "red"
            final_action = "🚨 [MADNESS] 강력 매도 경보\n\n- 주봉 RSI 80 돌파\n- 즉시 현금 비중 확대 필수."
        elif tqqq_rsi_wk >= 75:
            bg_color = "orange"
            final_action = "⚠️ [WARNING] 과열 경보\n\n- 주봉 RSI 75 돌파\n- 신규 매수 금지 및 리밸런싱."
        elif tqqq_mdd <= -50:
            bg_color = "green"
            final_action = "⚔️ [TOTAL WAR] 전면전 선포\n\n- MDD -50% 도달\n- 현금 100% 투입 (All-In)."
        elif tqqq_mdd <= -30:
            bg_color = "blue"
            final_action = "🛡️ [CRISIS LV2] 공포 구간\n\n- MDD -30% 도달\n- 현금 30% 투입."
        elif tqqq_mdd <= -20:
            bg_color = "blue"
            final_action = "🛡️ [CRISIS LV1] 조정 구간\n\n- MDD -20% 도달\n- 현금 20% 투입."
        else:
            bg_color = "gray"
            final_action = "✅ [NORMAL] 평시 운용\n\n- 월 적립금 투입\n- 정기 리밸런싱 수행."

        if bg_color == "red": st.error(final_action)
        elif bg_color == "orange": st.warning(final_action)
        elif bg_color == "green": st.success(final_action)
        elif bg_color == "blue": st.info(final_action)
        else: st.info(final_action)

if __name__ == "__main__":
    main()
