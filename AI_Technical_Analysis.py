import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import tempfile
import base64
import os
import requests

# Configure Streamlit page
st.set_page_config(layout="wide", page_title="AI-Powered Technical Stock Analysis")
st.title("AI-Powered Technical Stock Analysis Dashboard")

# Sidebar inputs
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Stock Symbol", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-14"))

def calculate_technical_indicators(data):
    # Calculate SMA
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    
    # Calculate EMA
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
    
    # Calculate Bollinger Bands
    rolling_mean = data['Close'].rolling(window=20).mean()
    rolling_std = data['Close'].rolling(window=20).std()
    data['BB_upper'] = rolling_mean + (rolling_std * 2)
    data['BB_lower'] = rolling_mean - (rolling_std * 2)
    
    # Calculate VWAP
    data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
    
    return data

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
        ["SMA 20", "SMA 50", "EMA 20", "Bollinger Bands", "VWAP"],
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
    
    # Update layout
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
    
    # Show the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Show recent data
    st.subheader("Recent Price Data")
    st.dataframe(data.tail(10), use_container_width=True)
    
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
