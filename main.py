import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# calculate trend momentum volatility and volume indicators
def calculate_indicators(df):
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Mid'] - (df['BB_Std'] * 2)
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    df['OBV_SMA'] = df['OBV'].rolling(window=20).mean()
    return df.dropna()

# generate signal values from latest indicator data
def generate_signals(latest_data):
    signals = {}
    if latest_data['SMA_20'] > latest_data['SMA_50']:
        signals['Trend'] = {'signal': 1, 'text': 'Bullish', 'value': 'SMA 20 > SMA 50'}
    elif latest_data['SMA_20'] < latest_data['SMA_50']:
        signals['Trend'] = {'signal': -1, 'text': 'Bearish', 'value': 'SMA 20 < SMA 50'}
    else:
        signals['Trend'] = {'signal': 0, 'text': 'Neutral', 'value': 'SMA 20 = SMA 50'}
    if latest_data['RSI'] > 60:
        signals['Momentum'] = {'signal': 1, 'text': 'Bullish', 'value': f"RSI: {latest_data['RSI']:.2f}"}
    elif latest_data['RSI'] < 40:
        signals['Momentum'] = {'signal': -1, 'text': 'Bearish', 'value': f"RSI: {latest_data['RSI']:.2f}"}
    else:
        signals['Momentum'] = {'signal': 0, 'text': 'Neutral', 'value': f"RSI: {latest_data['RSI']:.2f}"}
    if latest_data['Close'] > latest_data['BB_Upper']:
        signals['Volatility'] = {'signal': -1, 'text': 'Bearish (Overbought)', 'value': 'Price > Upper BB'}
    elif latest_data['Close'] < latest_data['BB_Lower']:
        signals['Volatility'] = {'signal': 1, 'text': 'Bullish (Oversold)', 'value': 'Price < Lower BB'}
    else:
        signals['Volatility'] = {'signal': 0, 'text': 'Neutral', 'value': 'Inside Bands'}
    if latest_data['OBV'] > latest_data['OBV_SMA']:
        signals['Volume'] = {'signal': 1, 'text': 'Bullish', 'value': 'OBV > 20-day OBV SMA'}
    elif latest_data['OBV'] < latest_data['OBV_SMA']:
        signals['Volume'] = {'signal': -1, 'text': 'Bearish', 'value': 'OBV < 20-day OBV SMA'}
    else:
        signals['Volume'] = {'signal': 0, 'text': 'Neutral', 'value': 'OBV Flat'}
    return signals

# calculate consensus score from signals and weights
def calculate_consensus_score(signals, weights):
    total_weight = sum(weights.values())
    weighted_sum = sum(signals[ind]['signal'] * weight for ind, weight in weights.items())
    score = (abs(weighted_sum) / total_weight) * 100
    direction = "Bullish" if weighted_sum > 0 else "Bearish" if weighted_sum < 0 else "Neutral"
    return round(score, 2), direction

# set up streamlit page configuration
st.set_page_config(page_title="Consensus Engine", layout="wide")
st.title("📊 Quantitative Consensus vs. Contradiction Engine")

# set up sidebar inputs
st.sidebar.header("Engine Parameters")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="RELIANCE.NS").upper()
period = st.sidebar.selectbox("Lookback Period", ["6mo", "1y", "2y"])
st.sidebar.subheader("Indicator Weights")
w_trend = st.sidebar.slider("Trend Weight", 1, 10, 5)
w_mom = st.sidebar.slider("Momentum Weight", 1, 10, 5)
w_volat = st.sidebar.slider("Volatility Weight", 1, 10, 5)
w_vol = st.sidebar.slider("Volume Weight", 1, 10, 5)
weights = {'Trend': w_trend, 'Momentum': w_mom, 'Volatility': w_volat, 'Volume': w_vol}

# run engine when button is clicked
if st.sidebar.button("Run Engine"):
    with st.spinner(f"Fetching data for {ticker}..."):
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            st.error("No data found. Please check the ticker symbol.")
        else:
            # flatten multiindex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            df = calculate_indicators(data)
            latest = df.iloc[-1]
            signals = generate_signals(latest)
            score, direction = calculate_consensus_score(signals, weights)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Final Consensus Score")
                st.metric(label=f"Directional Bias: {direction}", value=f"{score}%")
                if score >= 70:
                    st.success("✅ **EXECUTE TRADE** - Strong Market Consensus.")
                elif 40 <= score < 70:
                    st.warning("⚠️ **HOLD** - Weak Signal. Proceed with caution.")
                else:
                    st.error("🛑 **AVOID TRADE** - High Contradiction detected.")
            with col2:
                st.subheader("Indicator Matrix")
                matrix_data = {
                    "Indicator": ["Trend", "Momentum", "Volatility", "Volume"],
                    "Signal": [signals['Trend']['text'], signals['Momentum']['text'], signals['Volatility']['text'], signals['Volume']['text']],
                    "Raw Value": [signals['Trend']['value'], signals['Momentum']['value'], signals['Volatility']['value'], signals['Volume']['value']],
                    "Weight": [weights['Trend'], weights['Momentum'], weights['Volatility'], weights['Volume']]
                }
                st.table(pd.DataFrame(matrix_data))
            st.subheader(f"Price Action ({ticker})")
            st.line_chart(df['Close'])