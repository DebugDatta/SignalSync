# Quantitative Consensus vs Contradiction Engine

## Executive Summary

This engine is a systematic technical analysis tool that aggregates signals from four indicator categories (trend, momentum, volatility, volume) into a single normalized consensus score. The methodology eliminates discretionary decision making by applying fixed rule based thresholds and user defined preference weights to generate reproducible directional bias signals.

## Mathematical Notation

The following notation is used throughout this document:

- P_t: closing price at time t
- SMA_n: simple moving average over n periods
- RSI_n: relative strength index with n period lookback
- BB_k: Bollinger band with k standard deviations
- OBV_t: on balance volume at time t
- w_i: weight assigned to indicator category i
- S_i: signal value for indicator category i where S_i ∈ {-1, 0, 1}
- C: consensus score ∈ [0, 100]

---

## Indicator Specifications

### 1. Trend Indicators

#### Simple Moving Average (SMA)

**Definition:** The arithmetic mean of closing prices over a rolling window of n periods.

**Formula:**

SMA_n = (1/n) * Σ(P_t for t = t-n+1 to t)

**Properties:**
- Equally weights all observations in the window
- Introduces lag equal to (n-1)/2 periods
- Responds to price reversals only after n periods

**Configuration in this engine:**
- Short term window: n = 20
- Medium term window: n = 50

**Signal Derivation:**

S_trend = { +1 if SMA_20 > SMA_50
          { -1 if SMA_20 < SMA_50
          {  0 if SMA_20 = SMA_50

**Rationale:** The 20 and 50 period SMA crossover is a widely documented trend confirmation method. When the short term average exceeds the medium term average, upward price momentum is implied.

---

### 2. Momentum Indicators

#### Relative Strength Index (RSI)

**Definition:** A bounded oscillator (0 to 100) measuring the ratio of average gains to average losses over a lookback window. It quantifies the magnitude and velocity of recent price changes.

**Computation Algorithm:**

Step 1: Calculate price changes
Δ_t = P_t - P_{t-1}

Step 2: Separate gains and losses
gain_t = max(Δ_t, 0)
loss_t = max(-Δ_t, 0)

Step 3: Compute smoothed averages using exponential moving average (EMA)
EMA_gain_n = (gain_t * α) + (EMA_gain_{t-1} * (1 - α))
EMA_loss_n = (loss_t * α) + (EMA_loss_{t-1} * (1 - α))

where α = 2 / (n + 1) is the smoothing constant

Step 4: Compute relative strength
RS_n = EMA_gain_n / EMA_loss_n

Step 5: Transform to index
RSI_n = 100 - (100 / (1 + RS_n))

**Properties:**
- RSI = 50 indicates average gains equal average losses
- RSI > 50 indicates upward momentum dominance
- RSI < 50 indicates downward momentum dominance
- Overbought threshold (70) suggests mean reversion probability
- Oversold threshold (30) suggests mean reversion probability

**Configuration in this engine:**
- Lookback period: n = 14
- Overbought threshold: 60
- Oversold threshold: 40
- Neutral band: 40 to 60

**Signal Derivation:**

S_momentum = { +1 if RSI_14 > 60
             { -1 if RSI_14 < 40
             {  0 if 40 <= RSI_14 <= 60

**Note:** The engine uses 40 and 60 as thresholds rather than the traditional 30 and 70 to generate more frequent signals in trending markets. This is a configurable parameter.

---

### 3. Volatility Indicators

#### Bollinger Bands (BB)

**Definition:** A band constructed by placing bands at ±k standard deviations around a center SMA line. The bands expand when volatility increases and contract when volatility decreases.

**Formulas:**

BB_Mid_n = SMA_n(P_t)                          // center line
BB_Std_n = sqrt((1/n) * Σ(P_t - BB_Mid_n)²)   // standard deviation
BB_Upper_n = BB_Mid_n + (k * BB_Std_n)        // upper band
BB_Lower_n = BB_Mid_n - (k * BB_Std_n)        // lower band

**Bandwidth metric (optional):**
BW_n = (BB_Upper_n - BB_Lower_n) / BB_Mid_n

**Configuration in this engine:**
- Lookback period: n = 20
- Standard deviation multiplier: k = 2
- These values match the original Bollinger specification

**Signal Derivation:**

S_volatility = { -1 if P_t > BB_Upper_20      // overbought condition
               { +1 if P_t < BB_Lower_20      // oversold condition
               {  0 otherwise                  // price inside bands

**Rationale:** The mean reversion assumption holds that prices reverting to the mean (inside the bands) represents equilibrium. When price exceeds the upper band, it suggests an overbought state where prices may revert downward. Conversely, price below the lower band suggests oversold conditions with potential upward reversion.

---

### 4. Volume Indicators

#### On Balance Volume (OBV)

**Definition:** A cumulative volume indicator that adds volume on up days and subtracts volume on down days. It measures the flow of volume relative to price movement.

**Formula:**

OBV_t = OBV_{t-1} + V_t * sign(P_t - P_{t-1})

where:
sign(P_t - P_{t-1}) = { +1 if P_t > P_{t-1}
                       { -1 if P_t < P_{t-1}
                       {  0 if P_t = P_{t-1}

**Alternative formulation:**
OBV_t = Σ(V_t * sign(P_t - P_{t-1})) for t = 1 to current

**Smoothed OBV signal:**
OBV_SMA_n = SMA_n(OBV_t) with window n = 20

**Signal Derivation:**

S_volume = { +1 if OBV_t > OBV_SMA_20
            { -1 if OBV_t < OBV_SMA_20
            {  0 if OBV_t = OBV_SMA_20

**Rationale:** OBV leading price suggests volume confirms the trend. When price rises but OBV falls, divergence indicates the price move lacks volume support and may reverse.

---

## Consensus Score Aggregation

### Signal Normalization

Each indicator category produces a discrete signal S_i ∈ {-1, 0, 1}. This mapping eliminates the scale differences between indicators and standardizes the output space.

### Weighted Aggregation

The aggregated directional score is computed as:

weighted_sum = Σ(w_i * S_i) for i in {trend, momentum, volatility, volume}

total_weight = Σ(w_i) for i in {trend, momentum, volatility, volume}

### Consensus Score Formula

C = (|weighted_sum| / total_weight) * 100

**Properties:**
- C ∈ [0, 100]
- C = 100 indicates perfect consensus (all indicators aligned with maximum weights)
- C = 0 indicates perfect contradiction (indicators cancel out)
- C is always non negative because absolute value preserves direction information in the numerator while normalizing by total weight

### Directional Bias

The sign of weighted_sum determines the directional bias:

direction = { "bullish" if weighted_sum > 0
           { "bearish" if weighted_sum < 0
           { "neutral"  if weighted_sum = 0

### Signal Interpretation Matrix

| Consensus Score Range | Signal        | Recommended Action                    |
|-----------------------|---------------|---------------------------------------|
| C >= 70               | Strong Buy    | Execute long position                |
| 40 <= C < 70          | Weak Signal   | Hold with caution, require confirmation |
| C < 40                | High Conflict | Avoid position, wait for clarity      |

---

## Computational Algorithm

```
procedure run_analysis(ticker, period, weights):
    1. data = fetch_market_data(ticker, period)
    2. df = flatten_columns_if_multiindex(data)
    3. df = calculate_all_indicators(df)
    4. latest = df.iloc[-1]
    5. signals = generate_signals(latest)
    6. score, direction = calculate_consensus_score(signals, weights)
    7. render_dashboard(score, direction, signals)
```

**Time complexity:** O(n * m) where n = number of periods and m = number of indicators
**Space complexity:** O(n) for storing the dataframe

---

## Data Requirements

### Input Data Structure

| Column     | Type      | Description                        |
|------------|-----------|-------------------------------------|
| Open       | float64   | Opening price                       |
| High       | float64   | Highest price in period             |
| Low        | float64   | Lowest price in period              |
| Close      | float64   | Closing price                       |
| Volume     | float64   | Trading volume                      |

### Minimum Data Points Required

- SMA 50 requires at least 50 periods of data
- RSI 14 requires at least 14 periods of data
- Bollinger 20 requires at least 20 periods of data
- OBV SMA 20 requires at least 20 periods of data
- Overall minimum: 50 periods recommended

### Lookback Periods Available

- 6mo: approximately 126 trading days (6 months * 21 trading days per month)
- 1y: approximately 252 trading days
- 2y: approximately 504 trading days

---

## Default Configuration

| Parameter           | Default Value | Range   | Description                          |
|---------------------|---------------|---------|--------------------------------------|
| Default ticker      | RELIANCE.NS   | string  | NSE listed equity                    |
| Lookback period     | 6mo           | enum    | Data retrieval window                |
| Weight trend        | 5             | 1 to 10 | Preference for SMA crossover signals |
| Weight momentum     | 5             | 1 to 10 | Preference for RSI signals           |
| Weight volatility   | 5             | 1 to 10 | Preference for Bollinger band signals |
| Weight volume       | 5             | 1 to 10 | Preference for OBV signals            |

---

## Glossary

| Term              | Definition                                                               |
|-------------------|------------------------------------------------------------------------|
| Alpha             | Excess return relative to benchmark                                      |
| Backtest          | Testing a strategy on historical data                                   |
| Bollinger Band    | Volatility band placed at ±2 standard deviations around SMA            |
| EMA               | Exponential moving average with exponentially decaying weights          |
| Mean Reversion    | Assumption that prices revert to average over time                      |
| Multiindex        | Pandas column structure returned by Yfinance for multiple data sources  |
| Overbought        | Condition where price has risen excessively (RSI > 60)                 |
| Oversold          | Condition where price has declined excessively (RSI < 40)              |
| Regime            | Market state such as trending or ranging                                |
| Sharpe Ratio      | Risk adjusted return metric (return / standard deviation)              |
| Signal            | Directional indicator output (-1, 0, or +1)                            |
| SMA               | Simple moving average with equal weights                                |
| Win Rate          | Percentage of profitable trades                                         |

---

## Performance Metrics Definitions

### Win Rate

win_rate = (number of profitable trades / total trades) * 100

### Maximum Drawdown

max_drawdown = max((peak - trough) / peak) for all peaks

### Sharpe Ratio

sharpe = (mean return - risk free rate) / standard deviation of returns

---

## Limitations and Assumptions

1. **Market efficiency:** The engine assumes prices reflect all available information
2. **Stationarity:** Indicators assume price relationships remain stable over time
3. **Normal distribution:** Bollinger bands use standard deviation assuming normally distributed returns
4. **Mean reversion:** Volatility signals are based on the assumption that prices revert to the moving average
5. **Volume leading price:** OBV assumes volume changes precede price changes

---

## Future Development Roadmap

### Phase 1: Machine Learning Integration

**Implementation approach:**
- Train random forest or gradient boosting models on historical consensus scores
- Use features including indicator values, market regime classification, and sector correlation
- Target variable: n-day forward returns categorized as positive, negative, or neutral
- Validate using time series cross validation to prevent look ahead bias

**Expected outcome:** Adaptive threshold tuning based on historical indicator performance

### Phase 2: Sentiment Analysis Incorporation

**Implementation approach:**
- Integrate natural language processing pipeline for news headline analysis
- Aggregate sentiment scores using FinBERT or similar pretrained financial NLP models
- Treat sentiment as an additional weighted indicator category
- Normalize sentiment scores to -1, 0, 1 signal space

**Expected outcome:** Earlier signal generation by incorporating leading news data

### Phase 3: Adaptive Weighting System

**Implementation approach:**
- Implement regime detection using hidden Markov models or clustering
- Assign higher weights to momentum indicators during trending regimes
- Assign higher weights to mean reversion indicators during ranging regimes
- Recalculate weights on rolling 60 day lookback windows

**Expected outcome:** Automatic adaptation to current market conditions

### Phase 4: Multi Timeframe Analysis

**Implementation approach:**
- Run parallel analysis on daily, weekly, and monthly timeframes
- Aggregate signals using majority vote or weighted average
- Require at least 2 of 3 timeframes to agree for strong signal generation

**Expected outcome:** Higher confidence signals when multiple timeframes align

### Phase 5: Options Specific Signals

**Implementation approach:**
- Calculate implied volatility from options chain data
- Compute put call ratio as volume based indicator
- Generate probability of expiring in the money for specific strike prices
- Incorporate VIX as additional volatility indicator

**Expected outcome:** Signals specifically calibrated for options trading strategies

### Phase 6: Real Time Alert System

**Implementation approach:**
- Implement websocket connection for live price streaming
- Trigger alerts when consensus score crosses user defined thresholds
- Integrate with Telegram bot API for push notifications
- Store alert history in SQLite for pattern analysis

**Expected outcome:** Actionable notifications without continuous monitoring

### Phase 7: Portfolio Integration

**Implementation approach:**
- Connect to broker API using FIX protocol or REST API
- Implement position sizing based on Kelly criterion or risk parity
- Calculate portfolio level consensus across multiple holdings
- Track unrealized PnL and update signals in real time

**Expected outcome:** Automated execution based on consensus signals

### Phase 8: Backtesting Framework

**Implementation approach:**
- Implement vectorized backtesting for historical performance analysis
- Calculate walk forward accuracy metrics
- Generate equity curve, drawdown series, and trade log
- Compute annualized return, Sharpe ratio, maximum drawdown, and win rate

**Expected outcome:** Quantitative validation of strategy effectiveness

### Phase 9: Cryptocurrency Support

**Implementation approach:**
- Integrate with Binance or Coinbase API for crypto data
- Adapt lookback periods for 24/7 trading (use 30 day windows instead of calendar months)
- Incorporate exchange specific liquidity metrics
- Handle missing data due to exchange downtime

**Expected outcome:** Extension of consensus methodology to digital assets

### Phase 10: Sector Correlation Analysis

**Implementation approach:**
- Fetch sector index data (XLB, XLE, XLF, etc.) from Yfinance
- Compute relative strength of ticker vs sector
- Incorporate sector momentum as additional factor
- Weight sector analysis based on correlation strength

**Expected outcome:** Sector rotation signals for tactical asset allocation

---

## Technology Stack

| Library      | Version   | Purpose                           |
|--------------|-----------|-----------------------------------|
| Python       | 3.8+      | Programming language              |
| Streamlit    | latest    | Web interface framework           |
| Yfinance     | latest    | Market data retrieval             |
| Pandas       | latest    | Data manipulation and analysis    |
| NumPy        | latest    | Numerical computation             |

---

## Reproducibility Checklist

To replicate results:
1. Use the same ticker and lookback period
2. Set identical weight values for all four indicator categories
3. Ensure data source (Yfinance) returns unadjusted closing prices
4. Do not modify indicator calculation parameters (n, k values)
5. Use the same timestamp for data retrieval (Yfinance updates end of day)#   S i g n a l S y n c  
 