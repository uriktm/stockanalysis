# AI-Powered Technical Stock Analysis

An interactive Streamlit application for analyzing stocks using technical indicators and AI-powered insights.

## Features

- Real-time stock data fetching using yfinance
- Interactive candlestick charts with Plotly
- Technical indicators:
  - Simple Moving Averages (20 and 50-day)
  - Exponential Moving Average (20-day)
  - Bollinger Bands
  - Volume Weighted Average Price (VWAP)
- AI-powered technical analysis using LLaMA 2

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd AI_Technical_Analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run AI_Technical_Analysis.py
```

## Usage

1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
2. Select date range
3. Click "Fetch Data"
4. Choose technical indicators to display
5. Click "Run AI Analysis" for AI-powered insights

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt
