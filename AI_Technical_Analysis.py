import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import tempfile
import base64
import os
import requests
import ta

# Configure Streamlit page
st.set_page_config(layout="wide", page_title="AI-Powered Technical Stock Analysis")
st.title("AI-Powered Technical Stock Analysis Dashboard")

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
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    
    # Stochastic Oscillator
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
    df['Stoch_k'] = stoch.stoch()
    df['Stoch_d'] = stoch.stoch_signal()
    
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
            
            # Debug info
            st.sidebar.write("Data shape:", data.shape)
            
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
        current_price = data['Close'].iloc[-1]
        sma20 = data['SMA_20'].iloc[-1]
        sma50 = data['SMA_50'].iloc[-1]
        
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
        rsi = data['RSI'].iloc[-1]
        stoch_k = data['Stoch_k'].iloc[-1]
        
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
            # Save plot to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                fig.write_image(tmpfile.name)
                
                # Encode image to base64
                with open(tmpfile.name, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                
                # Clean up temporary file
                os.unlink(tmpfile.name)
                
                # Prepare prompt for AI
                prompt = f"""Analyze this stock chart for {ticker} and provide:
                1. Technical analysis of the price trends
                2. Key support and resistance levels
                3. Trading volume analysis
                4. Pattern recognition (if any)
                5. A clear buy/hold/sell recommendation
                
                Current Technical Indicators:
                - RSI: {rsi:.2f}
                - SMA20: ${sma20:.2f}
                - SMA50: ${sma50:.2f}
                - Stochastic %K: {stoch_k:.2f}
                
                Be specific and concise in your analysis."""
                
                # Send to Ollama API
                response = requests.post('http://localhost:11434/api/generate',
                                      json={
                                          "model": "llama2",
                                          "prompt": prompt,
                                          "stream": False
                                      })
                
                if response.status_code == 200:
                    analysis = response.json()['response']
                    st.write(analysis)
                else:
                    st.error("Error connecting to Ollama API. Make sure Ollama is running.")
                    
        except Exception as e:
            st.error(f"Error during AI analysis: {str(e)}")
