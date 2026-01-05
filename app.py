import streamlit as st
import streamlit.components.v1 as components

# --- 頁面配置 (全網頁寬度) ---
st.set_page_config(
    page_title="專業諧波形態雷達",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 自定義 CSS 樣式 (優化手機與電腦看圖體驗) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stExpander"] { border: none; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0b90b; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 標題 ---
st.title("🦅 幣安合約諧波雷達 (TradingView 整合版)")

# --- 側邊欄設定 ---
st.sidebar.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=40)
st.sidebar.header("市場篩選器")

# 預設熱門交易對清單
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

# 時區選擇 (連動到 TV Widget)
timeframe_map = {"15分鐘": "15", "1小時": "60", "4小時": "240", "1天": "D"}
selected_tf_label = st.sidebar.selectbox("分析時區", list(timeframe_map.keys()), index=1)
selected_tf = timeframe_map[selected_tf_label]

# --- TradingView 圖表組件函數 ---
def display_tradingview_chart(symbol, interval):
    """
    內嵌 TradingView 圖表，修正高度與寬度
    """
    # 確保符號格式正確 (BINANCE:BTCUSDT.P 代表期貨)
    tv_symbol = f"BINANCE:{symbol}.P"
    
    # HTML 小組件代碼
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
        "withdateranges": true,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "save_image": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "studies": [
          "RSI@tv-basicstudies",
          "StochasticRSI@tv-basicstudies",
          "MASimple@tv-basicstudies"
        ],
        "container_id": "tradingview_chart_widget"
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=710)

# --- 主畫面佈局 ---
selected_symbol = st.selectbox("🎯 請選擇要掃描的交易對", symbols)

# 分左右兩欄
col1, col2 = st.columns([4, 1])

with col1:
    st.markdown(f"#### {selected_symbol} - {selected_tf_label} 實時 K 線")
    display_tradingview_chart(selected_symbol, selected_tf)

with col2:
    st.markdown("### 🔍 諧波檢查指引")
    
    with st.expander("📌 比例對照表", expanded=True):
        st.write("**Bat (蝙蝠)**")
        st.caption("D點: XA 0.886 | B點: XA 0.382-0.5")
        st.write("**Gartley (加特利)**")
        st.caption("D點: XA 0.786 | B點: XA 0.618")
        st.write("**Crab (螃蟹)**")
        st.caption("D點: XA 1.618 | B點: XA 0.382-0.886")
        st.write("**Butterfly (蝴蝶)**")
        st.caption("D點: XA 1.27-1.618 | B點: XA 0.786")

    st.divider()
    
    # 幣安跳轉按鈕
    binance_url = f"https://www.binance.com/zh-TW/futures/{selected_symbol}"
    st.link_button("🚀 前往幣安下單 (Binance)", binance_url)
    
    st.divider()
    
    st.warning("💡 **小撇步**：\n點擊圖表上方的『技術指標』按鈕，搜尋『Harmonic』並點擊第一個指標，圖表會自動幫你畫出形態！")

# --- 底部形態速查圖 ---
st.markdown("---")
st.markdown("### 📖 諧波形態標準比例速查 (Cheat Sheet)")
st.image(
    "https://public.bnbstatic.com/image/cms/article/body/202209/78f1424361e687a71836171881519777.png", 
    caption="Harmonic Pattern Ratios Guide",
    use_container_width=True
)

st.caption("免責聲明：本工具僅供技術分析參考，不構成投資建議。")
