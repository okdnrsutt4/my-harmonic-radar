import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import plotly.graph_objects as go
from datetime import datetime
 
# --- 頁面美化配置 ---
st.set_page_config(page_title="諧波雷達專業版", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
 
st.title("🛡️ 幣安合約諧波形態雷達 (專業部署版)")
 
# --- 核心邏輯：多形態偵測 ---
def detect_harmonics(p):
    # p = [X, A, B, C, D]
    xa = abs(p[1] - p[0])
    ab = abs(p[2] - p[1])
    bc = abs(p[3] - p[2])
    ad = abs(p[4] - p[0])
    
    r_ab_xa = ab / xa if xa != 0 else 0
    r_ad_xa = ad / xa if xa != 0 else 0
    
    res = None
    # 1. Gartley: AB=0.618 XA, AD=0.786 XA
    if 0.55 <= r_ab_xa <= 0.65 and 0.75 <= r_ad_xa <= 0.82:
        res = "Gartley (加特利)"
    # 2. Bat: AB=0.382-0.5 XA, AD=0.886 XA
    elif 0.35 <= r_ab_xa <= 0.55 and 0.85 <= r_ad_xa <= 0.95:
        res = "Bat (蝙蝠)"
    # 3. Butterfly: AB=0.786 XA, AD=1.27-1.618 XA
    elif 0.70 <= r_ab_xa <= 0.85 and 1.20 <= r_ad_xa <= 1.65:
        res = "Butterfly (蝴蝶)"
    # 4. Crab: AB=0.382-0.886 XA, AD=1.618 XA
    elif 0.35 <= r_ab_xa <= 0.90 and 1.55 <= r_ad_xa <= 1.70:
        res = "Crab (螃蟹)"
        
    return res
 
def get_pivots(df, order=5):
    high_idx = argrelextrema(df.high.values, np.greater, order=order)[0]
    low_idx = argrelextrema(df.low.values, np.less, order=order)[0]
    pivots = []
    for i in high_idx: pivots.append({'type': 'high', 'price': df.high[i], 'index': i})
    for i in low_idx: pivots.append({'type': 'low', 'price': df.low[i], 'index': i})
    pivots.sort(key=lambda x: x['index'])
    return pivots[-5:]
 
# --- 側邊欄控制 ---
st.sidebar.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=50)
st.sidebar.header("掃描配置")
tf = st.sidebar.selectbox("時區 (Timeframe)", ['15m', '1h', '4h', '1d'], index=1)
limit_count = st.sidebar.slider("掃描交易對數量", 20, 100, 40)
error_margin = st.sidebar.slider("容錯率 (%)", 1, 15, 8) / 100
 
if st.sidebar.button("🔍 立即掃描全市場"):
    exchange = ccxt.binance({'options': {'defaultType': 'future'}})
    with st.spinner('正在分析幣安 K 線數據...'):
        markets = exchange.load_markets()
        symbols = [s for s in markets if '/USDT' in s and '_' not in s][:limit_count]
        
        found_data = []
        for symbol in symbols:
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
                df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
                pts = get_pivots(df)
                
                if len(pts) == 5:
                    p_prices = [pt['price'] for pt in pts]
                    name = detect_harmonics(p_prices)
                    if name:
                        side = "📈 多 (Bullish)" if p_prices[4] < p_prices[3] else "📉 空 (Bearish)"
                        found_data.append({"幣種": symbol, "形態": name, "方向": side, "最後價格": p_prices[4], "df": df, "pts": pts})
            except: continue
 
    if found_data:
        st.success(f"找到 {len(found_data)} 個符合形態的幣種！")
        for item in found_data:
            with st.expander(f"{item['幣種']} - {item['形態']} ({item['方向']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # 繪製 Plotly
                    df_plot = item['df']
                    pts = item['pts']
                    fig = go.Figure(data=[go.Candlestick(x=df_plot.index, open=df_plot['o'], high=df_plot['h'], low=df_plot['l'], close=df_plot['c'])])
                    fig.add_trace(go.Scatter(x=[p['index'] for p in pts], y=[p['price'] for p in pts],
                                             mode='lines+markers+text', text=['X','A','B','C','D'],
                                             line=dict(color='#00ff00' if "多" in item['方向'] else '#ff0000', width=2)))
                    fig.update_layout(height=400, margin=dict(l=0, r=0, b=0, t=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.metric("當前價格", f"{item['最後價格']:.4f}")
                    st.write(f"建議：請結合 RSI 或支撐位確認。")
    else:
        st.info("目前沒有發現符合比例的諧波形態。")
 
st.caption(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")