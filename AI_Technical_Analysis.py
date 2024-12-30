import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import tempfile
import base64
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from config import *  # Import all configuration settings

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv('OPENAI_BASE_URL', "https://api.openai.com/v1")
    )

# Configure Streamlit page
st.set_page_config(
    layout="wide",
    page_title=UI_CONFIG["PAGE_TITLE"],
    initial_sidebar_state=UI_CONFIG["INITIAL_SIDEBAR_STATE"]
)

# Add custom CSS for RTL support and better font readability
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Add custom CSS for RTL support and better font readability
st.markdown("""
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
""", unsafe_allow_html=True)

st.title(UI_CONFIG["PAGE_TITLE"])

# Sidebar inputs
st.sidebar.header("הגדרות")
ticker = st.sidebar.text_input("סמל המניה", value=DEFAULT_TICKER).upper()
start_date = st.sidebar.date_input("תאריך התחלה", value=pd.to_datetime(DEFAULT_START_DATE))
end_date = st.sidebar.date_input("תאריך סיום", value=pd.to_datetime(DEFAULT_END_DATE))

def calculate_technical_indicators(df):
    # Moving Averages
    for window in TECHNICAL_PARAMS["SMA_WINDOWS"]:
        df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
    for window in TECHNICAL_PARAMS["EMA_WINDOWS"]:
        df[f'EMA_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()
    
    # Bollinger Bands
    rolling_mean = df['Close'].rolling(window=TECHNICAL_PARAMS["BOLLINGER_PARAMS"]["WINDOW"]).mean()
    rolling_std = df['Close'].rolling(window=TECHNICAL_PARAMS["BOLLINGER_PARAMS"]["WINDOW"]).std()
    df['BB_upper'] = rolling_mean + (rolling_std * TECHNICAL_PARAMS["BOLLINGER_PARAMS"]["STD_DEV"])
    df['BB_lower'] = rolling_mean - (rolling_std * TECHNICAL_PARAMS["BOLLINGER_PARAMS"]["STD_DEV"])
    
    # VWAP
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=TECHNICAL_PARAMS["RSI_PERIOD"]).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=TECHNICAL_PARAMS["RSI_PERIOD"]).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=TECHNICAL_PARAMS["MACD_PARAMS"]["FAST"], adjust=False).mean()
    exp2 = df['Close'].ewm(span=TECHNICAL_PARAMS["MACD_PARAMS"]["SLOW"], adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=TECHNICAL_PARAMS["MACD_PARAMS"]["SIGNAL"], adjust=False).mean()
    
    # Stochastic Oscillator
    low_min = df['Low'].rolling(window=TECHNICAL_PARAMS["STOCH_PARAMS"]["PERIOD"]).min()
    high_max = df['High'].rolling(window=TECHNICAL_PARAMS["STOCH_PARAMS"]["PERIOD"]).max()
    df['Stoch_k'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    df['Stoch_d'] = df['Stoch_k'].rolling(window=TECHNICAL_PARAMS["STOCH_PARAMS"]["SMOOTH_K"]).mean()
    
    return df

# Fetch stock data
if st.sidebar.button("טען נתונים"):
    try:
        # Validate ticker
        if not ticker:
            st.error("אנא הזן סמל מניה")
        else:
            # Download data with error handling
            try:
                ticker_obj = yf.Ticker(ticker)
                data = ticker_obj.history(start=start_date, end=end_date)
                
                if data.empty:
                    st.error(f"לא נמצאו נתונים עבור {ticker}")
                else:
                    # Calculate indicators
                    data = calculate_technical_indicators(data)
                    st.session_state["stock_data"] = data
                    st.success(f"נטען בהצלחה נתונים עבור {ticker}")
            except Exception as e:
                st.error(f"שגיאה בטעינת הנתונים: בדוק שסמל המניה תקין")
                
    except Exception as e:
        st.error(f"שגיאה כללית: {str(e)}")

# Display data and charts
if "stock_data" in st.session_state:
    data = st.session_state["stock_data"]
    
    # Create main price chart
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC',
            showlegend=True
        )
    )
    
    # Sidebar: Select technical indicators
    st.sidebar.subheader("אינדיקטורים טכניים")
    indicators = st.sidebar.multiselect(
        "בחר אינדיקטורים",
        ["ממוצע נע פשוט 20", "ממוצע נע פשוט 50", "ממוצע נע מעריכי 20", "רצועות בולינגר", "VWAP", "RSI", "MACD", "סטוכסטי"],
        default=["ממוצע נע פשוט 20"]
    )
    
    # Add selected indicators
    if "ממוצע נע פשוט 20" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], name='ממוצע נע פשוט 20', line=dict(color='blue')))
    if "ממוצע נע פשוט 50" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], name='ממוצע נע פשוט 50', line=dict(color='orange')))
    if "ממוצע נע מעריכי 20" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], name='ממוצע נע מעריכי 20', line=dict(color='purple')))
    if "רצועות בולינגר" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], name='בולינגר עליון', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], name='בולינגר תחתון', line=dict(color='gray', dash='dash')))
    if "VWAP" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], name='VWAP', line=dict(color='green')))
        
    # Create subplot for additional indicators
    if any(ind in indicators for ind in ["RSI", "MACD", "סטוכסטי"]):
        fig2 = go.Figure()
        
        if "RSI" in indicators:
            fig2.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='blue')))
            fig2.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="מצב קניה (70)")
            fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="מצב מכירה (30)")
            
        if "MACD" in indicators:
            fig2.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')))
            fig2.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], name='Signal', line=dict(color='orange')))
            
        if "סטוכסטי" in indicators:
            fig2.add_trace(go.Scatter(x=data.index, y=data['Stoch_k'], name='Stoch %K', line=dict(color='blue')))
            fig2.add_trace(go.Scatter(x=data.index, y=data['Stoch_d'], name='Stoch %D', line=dict(color='orange')))
            fig2.add_hline(y=80, line_dash="dash", line_color="red")
            fig2.add_hline(y=20, line_dash="dash", line_color="green")
            
        fig2.update_layout(
            title="אינדיקטורים טכניים",
            height=300,
            showlegend=True,
            template='plotly_dark'
        )
        
    # Update main chart layout
    fig.update_layout(
        title=f'מחיר המניה {ticker}',
        yaxis_title='מחיר ($)',
        xaxis_title='תאריך',
        **CHART_STYLE
    )
    
    # Show the plots
    st.plotly_chart(fig, use_container_width=True)
    if any(ind in indicators for ind in ["RSI", "MACD", "סטוכסטי"]):
        st.plotly_chart(fig2, use_container_width=True)
    
    # Show recent data
    st.subheader("נתוני מחיר אחרונים")
    st.dataframe(data.tail(10), use_container_width=True)
    
    # Technical Analysis Summary
    st.subheader("סיכום ניתוח טכני")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**ממוצעים נעים**")
        current_price = float(data['Close'].iloc[-1])
        sma20 = float(data['SMA_20'].iloc[-1])
        sma50 = float(data['SMA_50'].iloc[-1])
        
        st.write(f"מחיר נוכחי: ${current_price:.2f}")
        st.write(f"ממוצע נע פשוט 20: ${sma20:.2f}")
        st.write(f"ממוצע נע פשוט 50: ${sma50:.2f}")
        
        if current_price > sma20 and current_price > sma50:
            st.write(" מחיר גבוה משני הממוצעים - Bullish")
        elif current_price < sma20 and current_price < sma50:
            st.write(" מחיר נמוך משני הממוצעים - Bearish")
        else:
            st.write(" מחיר בין שני הממוצעים - Neutral")
            
    with col2:
        st.write("**אינדיקטורי תנופה**")
        rsi = float(data['RSI'].iloc[-1])
        stoch_k = float(data['Stoch_k'].iloc[-1])
        
        st.write(f"RSI (14): {rsi:.2f}")
        if rsi > UI_CONFIG["THRESHOLDS"]["RSI"]["OVERBOUGHT"]:
            st.write(" RSI מצביע על מצב קניה")
        elif rsi < UI_CONFIG["THRESHOLDS"]["RSI"]["OVERSOLD"]:
            st.write(" RSI מצביע על מצב מכירה")
        else:
            st.write(" RSI מצביע על מצב נייטרלי")
            
        st.write(f"Stochastic %K: {stoch_k:.2f}")
        if stoch_k > UI_CONFIG["THRESHOLDS"]["STOCHASTIC"]["OVERBOUGHT"]:
            st.write(" Stochastic מצביע על מצב קניה")
        elif stoch_k < UI_CONFIG["THRESHOLDS"]["STOCHASTIC"]["OVERSOLD"]:
            st.write(" Stochastic מצביע על מצב מכירה")
        else:
            st.write(" Stochastic מצביע על מצב נייטרלי")
    
    # AI Analysis section
    st.subheader("ניתוח בינה מלאכותית")
    if st.button("בצע ניתוח בינה מלאכותית"):
        try:
            # Prepare chart data for analysis
            latest_data = data.tail(ANALYSIS_CONFIG["LOOKBACK_DAYS"])
            
            # Convert values to float for formatting
            current_price = float(data['Close'].iloc[-1])
            rsi_value = float(data['RSI'].iloc[-1])
            sma20_value = float(data['SMA_20'].iloc[-1])
            sma50_value = float(data['SMA_50'].iloc[-1])
            stoch_k_value = float(data['Stoch_k'].iloc[-1])
            macd_value = float(data['MACD'].iloc[-1])
            high_30d = float(latest_data['High'].max())
            low_30d = float(latest_data['Low'].min())
            avg_volume = int(latest_data['Volume'].mean())
            
            # Prepare prompt for GPT
            prompt = ANALYSIS_CONFIG["PROMPT_TEMPLATE"].format(
                ticker=ticker,
                current_price=current_price,
                rsi_value=rsi_value,
                sma20_value=sma20_value,
                sma50_value=sma50_value,
                stoch_k_value=stoch_k_value,
                macd_value=macd_value,
                high_30d=high_30d,
                low_30d=low_30d,
                avg_volume=avg_volume
            )
            
            # Get AI analysis
            response = client.chat.completions.create(
                model=OPENAI_CONFIG["MODEL"],
                messages=[
                    {"role": "system", "content": OPENAI_CONFIG["SYSTEM_PROMPT"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_CONFIG["TEMPERATURE"],
                max_tokens=OPENAI_CONFIG["MAX_TOKENS"]
            )
            
            # Display analysis
            analysis = response.choices[0].message.content
            st.markdown(f'<div class="ai-analysis">{analysis}</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"שגיאה במהלך ניתוח בינה מלאכותית: {str(e)}")
