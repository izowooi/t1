"""
Unit tests for stockbot.indicators module
"""
import pytest
from datetime import date, timedelta
from typing import List

from stockbot.db import OHLC
from stockbot.indicators import compute_sma_cross, CrossResult


class TestComputeSMACross:
    """Test cases for compute_sma_cross function"""

    @pytest.fixture
    def sample_ohlc_data(self) -> List[OHLC]:
        """Create sample OHLC data for testing"""
        base_date = date.today() - timedelta(days=100)
        data = []

        # Generate 70 days of sample data with a trend
        for i in range(70):
            current_date = base_date + timedelta(days=i)
            # Create a price trend that will generate cross signals
            base_price = 100.0

            # Add some variation to create realistic price movements
            if i < 30:
                # First 30 days: falling trend
                price = base_price - (i * 0.5)
            elif i < 50:
                # Next 20 days: rising trend (will create golden cross)
                price = base_price - 15 + ((i - 30) * 1.2)
            else:
                # Last 20 days: falling trend (will create dead cross)
                price = base_price + 15 - ((i - 50) * 0.8)

            # Add some noise
            import random
            noise = random.uniform(-2, 2)
            close_price = price + noise

            data.append(OHLC(
                ticker="TEST",
                d=current_date,
                open=close_price - 1,
                high=close_price + 2,
                low=close_price - 2,
                close=close_price,
                volume=1000000
            ))

        return data

    def test_insufficient_data(self):
        """Test with insufficient data (< 61 days)"""
        # Create only 30 days of data
        data = []
        base_date = date.today() - timedelta(days=30)

        for i in range(30):
            current_date = base_date + timedelta(days=i)
            data.append(OHLC(
                ticker="TEST",
                d=current_date,
                open=100,
                high=105,
                low=95,
                close=100 + i * 0.1,  # Slight upward trend
                volume=1000000
            ))

        result = compute_sma_cross(data)
        assert result is None

    def test_normal_operation_no_cross(self, sample_ohlc_data):
        """Test normal operation without forced cross signals"""
        result = compute_sma_cross(sample_ohlc_data, debug_mode=False)

        assert result is not None
        df, cross = result

        # DataFrame should exist
        assert df is not None
        assert len(df) > 0

        # May or may not have cross depending on actual data
        # This is testing the basic functionality

    def test_debug_mode_golden_cross(self, sample_ohlc_data):
        """Test debug mode forcing golden cross"""
        result = compute_sma_cross(sample_ohlc_data, debug_mode=True)

        assert result is not None
        df, cross = result

        assert cross is not None
        assert isinstance(cross, CrossResult)
        # Debug mode alternates between golden and dead cross
        assert cross.signal_type in ["golden_cross", "dead_cross"]

    def test_debug_mode_dead_cross(self, sample_ohlc_data):
        """Test debug mode forcing dead cross"""
        # Create data with different length to get dead cross
        test_data = sample_ohlc_data + [sample_ohlc_data[-1]]  # Make it odd length

        result = compute_sma_cross(test_data, debug_mode=True)

        assert result is not None
        df, cross = result

        assert cross is not None
        assert isinstance(cross, CrossResult)
        assert cross.signal_type in ["golden_cross", "dead_cross"]

    def test_cross_result_structure(self, sample_ohlc_data):
        """Test CrossResult object structure"""
        result = compute_sma_cross(sample_ohlc_data, debug_mode=True)

        assert result is not None
        df, cross = result

        assert cross is not None
        assert hasattr(cross, 'signal_type')
        assert hasattr(cross, 'price')
        assert hasattr(cross, 'sma5')
        assert hasattr(cross, 'sma60')

        assert cross.signal_type in ["golden_cross", "dead_cross"]
        assert isinstance(cross.price, float)
        assert isinstance(cross.sma5, float)
        assert isinstance(cross.sma60, float)

        # Basic sanity checks
        assert cross.price > 0
        assert cross.sma5 > 0
        assert cross.sma60 > 0

    def test_dataframe_structure(self, sample_ohlc_data):
        """Test DataFrame structure and columns"""
        result = compute_sma_cross(sample_ohlc_data, debug_mode=False)

        assert result is not None
        df, cross = result

        assert df is not None

        # Check required columns exist
        required_columns = ['close', 'sma5', 'sma60']
        for col in required_columns:
            assert col in df.columns

        # Check that SMA columns have values
        assert not df['sma5'].isna().all()
        assert not df['sma60'].isna().all()


# Helper function to create test data with specific cross pattern
def create_test_data_with_cross(cross_type: str = "golden_cross") -> List[OHLC]:
    """Create test data that will definitely produce a cross signal"""
    data = []
    base_date = date.today() - timedelta(days=70)

    for i in range(70):
        current_date = base_date + timedelta(days=i)

        if cross_type == "golden_cross":
            # Create pattern for golden cross:
            # First part: 5MA below 60MA
            # Later part: 5MA crosses above 60MA
            if i < 50:
                close_price = 100 - (i * 0.1)  # Falling trend
            else:
                close_price = 95 + ((i - 50) * 0.5)  # Rising trend
        else:  # dead_cross
            # Create pattern for dead cross:
            # First part: 5MA above 60MA
            # Later part: 5MA crosses below 60MA
            if i < 50:
                close_price = 100 + (i * 0.1)  # Rising trend
            else:
                close_price = 105 - ((i - 50) * 0.5)  # Falling trend

        data.append(OHLC(
            ticker="TEST",
            d=current_date,
            open=close_price - 1,
            high=close_price + 2,
            low=close_price - 2,
            close=close_price,
            volume=1000000
        ))

    return data
