# AI-Powered Technical Stock Analysis

An interactive Streamlit application for analyzing stocks using technical indicators and AI-powered insights.

## Features

### Technical Analysis
- Real-time stock data fetching using yfinance
- Interactive candlestick charts with Plotly
- Multiple technical indicators:
  - Simple Moving Averages (20 and 50-day)
  - Exponential Moving Average (20-day)
  - Bollinger Bands
  - Volume Weighted Average Price (VWAP)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
  - Stochastic Oscillator

### AI Analysis
- Automated technical analysis using LLaMA 2
- Pattern recognition
- Support and resistance level identification
- Trading volume analysis
- Buy/Hold/Sell recommendations

### Additional Features
- Technical Analysis Summary dashboard
- Real-time indicator calculations
- Overbought/Oversold signals
- Multiple timeframe analysis
- Interactive charts with zoom and pan capabilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/uriktm/stockanalysis.git
cd stockanalysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Ollama and the LLaMA 2 model:
```bash
# Download Ollama from https://ollama.ai/
ollama run llama2
```

4. Run the application:
```bash
streamlit run AI_Technical_Analysis.py
```

## Usage

1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL)
2. Select date range for analysis
3. Click "Fetch Data" to load stock information
4. Choose technical indicators to display
5. View the Technical Analysis Summary
6. Click "Run AI Analysis" for AI-powered insights

## Technical Indicators Guide

### Moving Averages
- SMA (Simple Moving Average): Shows the average price over a specific period
- EMA (Exponential Moving Average): Gives more weight to recent prices

### Momentum Indicators
- RSI (Relative Strength Index): Shows overbought/oversold conditions
- Stochastic Oscillator: Compares closing price to price range
- MACD: Shows trend direction and momentum

### Volume Indicators
- VWAP: Shows the average price weighted by volume

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
flake8
```

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt
- Ollama with LLaMA 2 model for AI analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
