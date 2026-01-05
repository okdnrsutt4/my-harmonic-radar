import streamlit as st
import ccxt
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import plotly.graph_objects as go
import time

# --- 頁面配置 ---
st.set_page_config(page_title="諧波雷達 - 穩定版", layout="wide")
st.title("🛡️ 幣安合約諧波雷達 (雲端兼容版)")

# --- 初始化幣安 (優化連線) ---
def get_exchange():
    return ccxt.binance({
        'options': {'defaultType': 'future'},
        'timeout': 30000,
        'enableRateLimit': True,
        # 使用備用網域避開 IP 屏蔽
        'urls': {
            'api': {
                'public': 'https://fapi.binance.com',
            }
        }
    })

# --- 核心算法 ---
def detect_harmonics(p):
    xa, ab, bc, ad = abs(p[1]-p[0]), abs(p[2]-p[1]), abs(p[3]-p[2]), abs(p[4]-p[0])
    r_ab_xa = ab / xa if xa != 0 else 0
    r_ad_xa = ad / xa if xa != 0 else 0
    
    if 0.382 <= r_ab_xa <= 0.618:
        if 0.76 <= r_ad_xa <= 0.82: return "Gartley (加特利)"
        if 0.86 <= r_ad_xa <= 0.92: return "Bat (蝙蝠)"
    if 0.70 <= r_ab_xa <= 0.95 and 1.2 <= r_ad_xa <= 1.6:
        return "Butterfly (蝴蝶)"
    return None

def get_pivots(df, order=5):
    high_idx = argrelextrema(df.high.values, np.greater, order=order)[0]
    low_idx = argrelextrema(df.low.values, np.less, order=order)[0]
    pivots = []
    for i in high_idx: pivots.append({'type': 'high', 'price': df.high[i], 'index': i})
    for i in low_idx: pivots.append({'type': 'low', 'price': df.low[i], 'index': i})
    pivots.sort(key=lambda x: x['index'])
    return pivots[-5:]

# --- UI 邏輯 ---
st.sidebar.header("控制面板")
tf = st.sidebar.selectbox("時區", ['1h', '4h', '1d'])
scan_count = st.sidebar.slider("掃描幣種數量", 10, 50, 30)

if st.sidebar.button("🚀 開始掃描"):
    exchange = get_exchange()
    try:
        with st.spinner('正在連線幣安 API...'):
            # 加入重試機制
            markets = None
            for _ in range(3):
                try:
                    markets = exchange.load_markets()
                    break
                except:
                    time.sleep(2)
            
            if not markets:
                st.error("❌ 無法連線至幣安。這通常是 Streamlit 伺服器 IP 限制，請嘗試重新整理或在本地執行。")
            else:
                symbols = [s for s in markets if '/USDT' in s and '_' not in s][:scan_count]
                found = False
                
                for symbol in symbols:
                    try:
                        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
                        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
                        pts = get_pivots(df)
                        if len(pts) == 5:
                            p_prices = [pt['price'] for pt in pts]
                            name = detect_harmonics(p_prices)
                            if name:
                                found = True
                                st.success(f"🎯 {symbol}: {name}")
                                # 畫圖代碼 (省略部分以保持簡潔，同前一版)
                                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['o'], high=df['h'], low=df['l'], close=df['c'])])
                                fig.add_trace(go.Scatter(x=[p['index'] for p in pts], y=[p['price'] for p in pts], mode='lines+markers+text', text=['X','A','B','C','D'], line=dict(color='yellow')))
                                fig.update_layout(template="plotly_dark", height=400)
                                st.plotly_chart(fig, use_container_width=True)
                    except: continue
                if not found: st.info("目前無符合形態。")
    except Exception as e:
        st.error(f"發生未預期錯誤: {e}")