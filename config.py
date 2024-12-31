from datetime import datetime, timedelta

# Default settings
DEFAULT_TICKER = "AAPL"
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")

# Technical Analysis Parameters
TECHNICAL_PARAMS = {
    "SMA_WINDOWS": [20, 50],
    "EMA_WINDOWS": [20],
    "RSI_PERIOD": 14,
    "MACD_PARAMS": {
        "FAST": 12,
        "SLOW": 26,
        "SIGNAL": 9
    },
    "STOCH_PARAMS": {
        "PERIOD": 14,
        "SMOOTH_K": 3
    },
    "BOLLINGER_PARAMS": {
        "WINDOW": 20,
        "STD_DEV": 2
    }
}

# UI Settings
UI_CONFIG = {
    "PAGE_TITLE": "ניתוח טכני של מניות מבוסס בינה מלאכותית",
    "INITIAL_SIDEBAR_STATE": "expanded",
    "CHART_HEIGHTS": {
        "MAIN": 600,
        "SECONDARY": 300
    },
    "DEFAULT_INDICATORS": ["ממוצע נע פשוט 20"],
    "COLORS": {
        "SMA20": "blue",
        "SMA50": "orange",
        "EMA20": "purple",
        "BOLLINGER": "gray",
        "VWAP": "green",
        "MACD": "blue",
        "MACD_SIGNAL": "orange",
        "STOCH_K": "blue",
        "STOCH_D": "orange"
    },
    "THRESHOLDS": {
        "RSI": {
            "OVERBOUGHT": 70,
            "OVERSOLD": 30
        },
        "STOCHASTIC": {
            "OVERBOUGHT": 80,
            "OVERSOLD": 20
        }
    }
}

# Chart Style Settings
CHART_STYLE = {
    "template": "plotly_dark",
    "legend": {
        "yanchor": "top",
        "y": 0.99,
        "xanchor": "right",
        "x": 0.99
    },
    "margin": {
        "l": 50,
        "r": 50,
        "t": 50,
        "b": 50
    }
}

# OpenAI Settings
OPENAI_CONFIG = {
    "MODEL": "gpt-4o",
    "TEMPERATURE": 0.7,
    "MAX_TOKENS": 1500,
    "SYSTEM_PROMPT": "You are a professional stock market analyst. Provide clear, concise, and actionable analysis based on technical indicators and market data."
}

# Analysis Settings
ANALYSIS_CONFIG = {
    "LOOKBACK_DAYS": 30,  # Days of data to consider for recent analysis
    "PROMPT_TEMPLATE": """נתוח את נתוני המניה של {ticker} וספק:
1. ניתוח טכני של מגמות המחיר
2. רמות תמיכה והתנגדות מפתחות
3. ניתוח נפח המסחר
4. זיהוי דפוסים (אם קיימים)
5. המלצה ברורה לקניה/החזקה/מכירה

אינדיקטורים טכניים נוכחיים:
- מחיר: ${current_price:.2f}
- RSI (14): {rsi_value:.2f}
- SMA20: ${sma20_value:.2f}
- SMA50: ${sma50_value:.2f}
- Stochastic %K: {stoch_k_value:.2f}
- MACD: {macd_value:.2f}

פעולת מחיר אחרונה:
- שיא 30 יום: ${high_30d:.2f}
- מינימום 30 יום: ${low_30d:.2f}
- ממוצע נפח: {avg_volume:,}

אנא ספק ניתוח מקצועי, קונציזי ומעשי. תשובה בעברית!"""
}

# Custom CSS
CUSTOM_CSS = """
    <style>
        body {
            direction: rtl;
            font-family: 'Rubik', 'Assistant', sans-serif;
        }
        .stButton button {
            direction: rtl;
            font-family: 'Rubik', 'Assistant', sans-serif;
        }
        .stTextInput input {
            direction: rtl;
            font-family: 'Rubik', 'Assistant', sans-serif;
        }
        .css-1d391kg {
            direction: rtl;
        }
        div[data-testid="stSidebarNav"] {
            direction: rtl;
        }
        .ai-analysis {
            font-family: 'Rubik', 'Assistant', sans-serif;
            font-size: 1.1rem;
            line-height: 1.6;
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            border: 1px solid #333;
        }
        .ai-analysis p {
            margin-bottom: 15px;
        }
    </style>
"""
