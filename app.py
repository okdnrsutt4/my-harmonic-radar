import streamlit as st
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(
    page_title="專業諧波形態雷達",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 自定義 CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0b90b; color: black; font-weight: bold; }
    .stLinkButton>a { width: 100%; border-radius: 5px; text-align: center; background-color: #2962ff; color: white !important; font-weight: bold; text-decoration: none; display: inline-block; line-height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 幣安合約諧波雷達 (推薦方案版)")

# --- 側邊欄設定 ---
st.sidebar.header("市場篩選器")
hot_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT"]
alt_symbols = ["ORDIUSDT", "TIAUSDT", "LINKUSDT", "NEARUSDT", "SUIUSDT", "PEPEUSDT", "WIFUSDT", "FETUSDT"]

category = st.sidebar.radio("選擇幣種板塊", ["熱門幣種", "強勢山寨", "自定義輸入"])

if category == "熱門幣種":
    symbols = hot_symbols
elif category == "強勢山寨":
    symbols = alt_symbols
else:
    custom_input = st.sidebar.text_input("輸入幣種符號 (用逗號隔開)", "BTCUSDT,ETHUSDT")
    symbols = [s.strip().upper() for s in custom_input.split(",")]

timeframe_map = {"15分鐘": "15", "1小時": "60", "4小時": "240", "1天": "D"}
selected_tf_label = st.sidebar.selectbox("分析時區", list(timeframe_map.keys()), index=1)
selected_tf = timeframe_map[selected_tf_label]

# --- TradingView 函數 ---
def display_tradingview_chart(symbol, interval):
    tv_symbol = f"BINANCE:{symbol}.P"
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:700px; width:100%;">
      <div id="tradingview_chart_widget" style="height:700px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{interval}",
        "timezone": "Asia/Taipei",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "studies": [
          "RSI@tv-basicstudies",
          "ZigZag@tv-basicstudies"  // 推薦方案：自動預載高低點連線
        ],
        "container_id": "tradingview_chart_widget"
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=710)

# --- 主畫面佈局 ---
selected_symbol = st.selectbox("🎯 請選擇要掃描的交易對", symbols)

col1, col2 = st.columns([4, 1])

with col1:
    st.markdown(f"#### {selected_symbol} - {selected_tf_label} 實時 K 線")
    display_tradingview_chart(selected_symbol, selected_tf)

with col2:
    st.markdown("### 🔍 分析工具箱")
    
    # 新增：跳轉到 TV 完整版搜尋指標
    tv_full_url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{selected_symbol}.P"
    st.link_button("📈 完整版圖表 (搜指標)", tv_full_url)
    
    st.divider()
    
    with st.expander("📌 諧波比例對照", expanded=True):
        st.write("**Bat (蝙蝠)**: D: 0.886")
        st.write("**Gartley (加特利)**: D: 0.786")
        st.write("**Crab (螃蟹)**: D: 1.618")
        st.write("**Butterfly (蝴蝶)**: D: 1.27")

    st.divider()
    
    binance_url = f"https://www.binance.com/zh-TW/futures/{selected_symbol}"
    st.markdown(f'<a href="{binance_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:5px; height:3em; background-color:#f0b90b; color:black; font-weight:bold; border:none; cursor:pointer;">🚀 前往幣安下單</button></a>', unsafe_allow_html=True)
    
    st.divider()
    st.info("💡 圖表已預載 ZigZag (折線)，方便你對齊 XABCD 頂點。")

# --- 底部形態速查圖 ---
st.image("https://public.bnbstatic.com/image/cms/article/body/202209/78f1424361e687a71836171881519777.png", use_container_width=True)
