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

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = "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"
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.openai.com/v1"
    )

# Configure Streamlit page
st.set_page_config(layout="wide", page_title="AI-Powered Technical Stock Analysis")
st.title("AI-Powered Technical Stock Analysis Dashboard")

# Add API Key input in sidebar if not in environment
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", key="openai_api_key", 
                         help="Enter your OpenAI API key to enable AI analysis")
    if api_key:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1"
        )

# Sidebar inputs
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Symbol", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-14"))

def calculate_technical_indicators(df):
    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # Bollinger Bands
    rolling_mean = df['Close'].rolling(window=20).mean()
    rolling_std = df['Close'].rolling(window=20).std()
    df['BB_upper'] = rolling_mean + (rolling_std * 2)
    df['BB_lower'] = rolling_mean - (rolling_std * 2)
    
    # VWAP
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Stochastic Oscillator
    low_min = df['Low'].rolling(window=14).min()
    high_max = df['High'].rolling(window=14).max()
    df['Stoch_k'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    df['Stoch_d'] = df['Stoch_k'].rolling(window=3).mean()
    
    return df

# Fetch stock data
if st.sidebar.button("Fetch Data"):
    try:
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.error(f"No data found for {ticker}")
        else:
            # Calculate indicators
            data = calculate_technical_indicators(data)
            st.session_state["stock_data"] = data
            st.success(f"Successfully loaded data for {ticker}")
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

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
    st.sidebar.subheader("Technical Indicators")
    indicators = st.sidebar.multiselect(
        "Select indicators",
        ["SMA 20", "SMA 50", "EMA 20", "Bollinger Bands", "VWAP", "RSI", "MACD", "Stochastic"],
        default=["SMA 20"]
    )
    
    # Add selected indicators
    if "SMA 20" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], name='SMA 20', line=dict(color='blue')))
    if "SMA 50" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50', line=dict(color='orange')))
    if "EMA 20" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA_20'], name='EMA 20', line=dict(color='purple')))
    if "Bollinger Bands" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_upper'], name='BB Upper', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=data.index, y=data['BB_lower'], name='BB Lower', line=dict(color='gray', dash='dash')))
    if "VWAP" in indicators:
        fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], name='VWAP', line=dict(color='green')))
        
    # Create subplot for additional indicators
    if any(ind in indicators for ind in ["RSI", "MACD", "Stochastic"]):
        fig2 = go.Figure()
        
        if "RSI" in indicators:
            fig2.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='blue')))
            fig2.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
            fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
            
        if "MACD" in indicators:
            fig2.add_trace(go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')))
            fig2.add_trace(go.Scatter(x=data.index, y=data['MACD_signal'], name='Signal', line=dict(color='orange')))
            
        if "Stochastic" in indicators:
            fig2.add_trace(go.Scatter(x=data.index, y=data['Stoch_k'], name='Stoch %K', line=dict(color='blue')))
            fig2.add_trace(go.Scatter(x=data.index, y=data['Stoch_d'], name='Stoch %D', line=dict(color='orange')))
            fig2.add_hline(y=80, line_dash="dash", line_color="red")
            fig2.add_hline(y=20, line_dash="dash", line_color="green")
            
        fig2.update_layout(
            title="Technical Indicators",
            height=300,
            showlegend=True,
            template='plotly_dark'
        )
        
    # Update main chart layout
    fig.update_layout(
        title=f'{ticker} Stock Price',
        yaxis_title='Price ($)',
        xaxis_title='Date',
        template='plotly_dark',
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Show the plots
    st.plotly_chart(fig, use_container_width=True)
    if any(ind in indicators for ind in ["RSI", "MACD", "Stochastic"]):
        st.plotly_chart(fig2, use_container_width=True)
    
    # Show recent data
    st.subheader("Recent Price Data")
    st.dataframe(data.tail(10), use_container_width=True)
    
    # Technical Analysis Summary
    st.subheader("Technical Analysis Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Moving Averages**")
        current_price = float(data['Close'].iloc[-1])
        sma20 = float(data['SMA_20'].iloc[-1])
        sma50 = float(data['SMA_50'].iloc[-1])
        
        st.write(f"Current Price: ${current_price:.2f}")
        st.write(f"SMA 20: ${sma20:.2f}")
        st.write(f"SMA 50: ${sma50:.2f}")
        
        if current_price > sma20 and current_price > sma50:
            st.write(" Price is above both moving averages - Bullish")
        elif current_price < sma20 and current_price < sma50:
            st.write(" Price is below both moving averages - Bearish")
        else:
            st.write(" Price is between moving averages - Neutral")
            
    with col2:
        st.write("**Momentum Indicators**")
        rsi = float(data['RSI'].iloc[-1])
        stoch_k = float(data['Stoch_k'].iloc[-1])
        
        st.write(f"RSI (14): {rsi:.2f}")
        if rsi > 70:
            st.write(" RSI indicates overbought conditions")
        elif rsi < 30:
            st.write(" RSI indicates oversold conditions")
        else:
            st.write(" RSI indicates neutral conditions")
            
        st.write(f"Stochastic %K: {stoch_k:.2f}")
        if stoch_k > 80:
            st.write(" Stochastic indicates overbought conditions")
        elif stoch_k < 20:
            st.write(" Stochastic indicates oversold conditions")
        else:
            st.write(" Stochastic indicates neutral conditions")
    
    # AI Analysis section
    st.subheader("AI-Powered Analysis")
    if st.button("Run AI Analysis"):
        try:
            if not api_key:
                st.error("Please enter your OpenAI API key in the sidebar to use AI analysis")
            else:
                # Prepare chart data for analysis
                latest_data = data.tail(30)  # Last 30 days for recent analysis
                
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
                prompt = f"""Analyze this stock data for {ticker} and provide:
                1. Technical analysis of the price trends
                2. Key support and resistance levels
                3. Trading volume analysis
                4. Pattern recognition (if any)
                5. A clear buy/hold/sell recommendation
                
                Current Technical Indicators:
                - Price: ${current_price:.2f}
                - RSI (14): {rsi_value:.2f}
                - SMA20: ${sma20_value:.2f}
                - SMA50: ${sma50_value:.2f}
                - Stochastic %K: {stoch_k_value:.2f}
                - MACD: {macd_value:.2f}
                
                Recent price action:
                - 30-day high: ${high_30d:.2f}
                - 30-day low: ${low_30d:.2f}
                - Average volume: {avg_volume:,}
                
                Please provide a concise, professional analysis. Answer in Hebrew!."""
                
                # Get AI analysis
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a professional stock market analyst. Provide clear, concise, and actionable analysis based on technical indicators and market data."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                # Display analysis
                analysis = response.choices[0].message.content
                st.write(analysis)
                
        except Exception as e:
            st.error(f"Error during AI analysis: {str(e)}")
