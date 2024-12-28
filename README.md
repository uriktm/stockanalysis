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
- Advanced technical analysis using OpenAI's GPT-4
- Intelligent pattern recognition
- Support and resistance level identification
- Trading volume analysis
- Data-driven Buy/Hold/Sell recommendations
- Comprehensive market context analysis

### Additional Features
- Technical Analysis Summary dashboard
- Real-time indicator calculations
- Overbought/Oversold signals
- Multiple timeframe analysis
- Interactive charts with zoom and pan capabilities
- RTL support for Hebrew interface

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

3. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

Run the application using Streamlit:
```bash
streamlit run AI_Technical_Analysis.py
```

The application will open in your default web browser at http://localhost:8501

## Features in Detail

### Technical Indicators
- **Moving Averages**: Track trend direction and potential support/resistance levels
- **Bollinger Bands**: Identify volatility and potential price breakouts
- **RSI**: Measure momentum and overbought/oversold conditions
- **MACD**: Signal potential trend changes and momentum
- **VWAP**: Determine intraday price action and liquidity levels
- **Stochastic Oscillator**: Identify potential reversal points

### AI Analysis
The GPT-4 powered analysis provides:
- Comprehensive technical analysis interpretation
- Pattern recognition and trend analysis
- Support and resistance level identification
- Volume analysis and its implications
- Market sentiment assessment
- Actionable trading insights

## Requirements
- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## License
MIT License - see LICENSE file for details
