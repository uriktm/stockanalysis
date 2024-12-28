import pytest
import pandas as pd
import numpy as np
from AI_Technical_Analysis import calculate_technical_indicators

@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    data = pd.DataFrame({
        'Open': np.random.randn(len(dates)) + 100,
        'High': np.random.randn(len(dates)) + 101,
        'Low': np.random.randn(len(dates)) + 99,
        'Close': np.random.randn(len(dates)) + 100,
        'Volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    return data

def test_sma_calculation(sample_data):
    result = calculate_technical_indicators(sample_data)
    assert 'SMA_20' in result.columns
    assert 'SMA_50' in result.columns
    assert not result['SMA_20'].isna().all()
    assert not result['SMA_50'].isna().all()

def test_ema_calculation(sample_data):
    result = calculate_technical_indicators(sample_data)
    assert 'EMA_20' in result.columns
    assert not result['EMA_20'].isna().all()

def test_bollinger_bands(sample_data):
    result = calculate_technical_indicators(sample_data)
    assert 'BB_upper' in result.columns
    assert 'BB_lower' in result.columns
    assert not result['BB_upper'].isna().all()
    assert not result['BB_lower'].isna().all()
    assert (result['BB_upper'] >= result['BB_lower']).all()

def test_vwap_calculation(sample_data):
    result = calculate_technical_indicators(sample_data)
    assert 'VWAP' in result.columns
    assert not result['VWAP'].isna().all()
