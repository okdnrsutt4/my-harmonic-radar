import streamlit as st
import streamlit.components.v1 as components

# --- 頁面配置 ---
st.set_page_config(page_title="諧波雷達 x TradingView", layout="wide")

st.title("🦅 幣安合約全市場雷達 (TradingView 整合版)")

# --- 側邊欄：選擇要觀察的幣種 ---
st.sidebar.header("市場篩選")
category = st.sidebar.selectbox("板塊", ["熱門幣種", "強勢山寨", "自定義"])

# 這裡預設一些熱門合約，避免 API 封鎖導致完全沒東西看
if category == "熱門幣種":
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT", "XRPUSDT"]
elif category == "強勢山寨":
    symbols = ["ORDIUSDT", "TIAUSDT", "LINKUSDT", "AVAXUSDT", "NEARUSDT", "SUIUSDT"]
else:
    custom_input = st.sidebar.text_input("輸入幣種 (例如: BTCUSDT,ETHUSDT)", "BTCUSDT")
    symbols = [s.strip() for s in custom_input.split(",")]

# --- TradingView 圖表組件功能 ---
def display_tradingview_chart(symbol):
    """內嵌 TradingView 圖表小組件"""
    # 這裡加入了一些專業指標，包括自動成交量、RSI 等
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:600px;">
      <div id="tradingview_xxxx"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "BINANCE:{symbol}.P",  // .P 代表期貨永續合約
        "interval": "60",
        "timezone": "Asia/Taipei",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
        "studies": [
          "RSI@tv-basicstudies",
          "MASimple@tv-basicstudies"
        ],
        "container_id": "tradingview_xxxx"
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=600)

# --- 主介面佈局 ---
# 建立一個選單讓使用者點擊要查看的幣種
selected_symbol = st.selectbox("🎯 選擇要分析的交易對", symbols)

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"### {selected_symbol} 實時分析圖表")
    display_tradingview_chart(selected_symbol)

with col2:
    st.markdown("### 🔍 諧波檢查表")
    st.info("請在 TradingView 圖表中觀察以下比例：")
    st.write("- **Bat (蝙蝠)**: D點回撤 XA 0.886")
    st.write("- **Gartley (加特利)**: D點回撤 XA 0.786")
    st.write("- **Crab (螃蟹)**: D點回撤 XA 1.618")
    
    st.divider()
    
    # 這裡可以加入快速跳轉到幣安交易頁面的連結
    binance_url = f"https://www.binance.com/zh-TC/futures/{selected_symbol}"
    st.link_button("🚀 前往幣安下單", binance_url)
    
    st.divider()
    st.warning("提醒：諧波形態需配合 RSI 背離或關鍵支撐壓力位使用，勝率更高。")

# --- 底部：全市場掃描清單（選填） ---
st.markdown("---")
st.subheader("📊 形態特徵速查")
st.image("https://www.tradingpedia.com/wp-content/uploads/2015/05/harmonic-patterns-cheat-sheet.jpg", caption="諧波形態比例參考圖")
