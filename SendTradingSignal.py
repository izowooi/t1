#Trend Following
import os

import yfinance as yf
import pandas as pd

from SendEmail import send_email
from SendTelegram import send_telegram

def calculate_moving_averages(data, short_window=5, long_window=60):
    """
    Calculate short-term and long-term moving averages.
    :param data: DataFrame with 'Close' prices
    :param short_window: Window for short-term moving average
    :param long_window: Window for long-term moving average
    :return: DataFrame with moving averages
    """
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    return data

def generate_signals(data):
    """
    Generate buy and sell signals based on moving averages.
    :param data: DataFrame with moving averages
    :return: DataFrame with signals
    """
    data['Buy_Signal'] = (data['Short_MA'] > data['Long_MA']) & (data['Short_MA'].shift(1) <= data['Long_MA'].shift(1))
    data['Sell_Signal'] = (data['Short_MA'] < data['Long_MA']) & (data['Short_MA'].shift(1) >= data['Long_MA'].shift(1))
    return data

def send_trading_signal_alert(ticker):
    print(f'매매 신호 확인: {ticker}')
    data = yf.download(ticker, start='2020-01-01')

    # 이동 평균 계산
    data = calculate_moving_averages(data, short_window=5, long_window=60)

    # 매매 신호 생성
    data = generate_signals(data)

    # 결과 확인
    print(data[['Close', 'Short_MA', 'Long_MA', 'Buy_Signal', 'Sell_Signal']].tail(n=60))

    # 결과 확인 및 알림 전송
    #latest_data = data.iloc[-1][['Buy_Signal', 'Sell_Signal']]  # 가장 최근 데이터
    latest_data = data.iloc[-1]# 가장 최근 데이터
    print('\n')
    print(latest_data)

    receiver_email = 'izowooi85@gmail.com'

    dotenv_path = os.getenv('dotenv_path', '.env')

    print(f'dotenv_path의 값: {dotenv_path}')

    test_buy_signal = os.getenv('test_send_email', False)

    if test_buy_signal:
        latest_data['Buy_Signal'] = True

    print(f'dotenv_path의 값: {dotenv_path}')

    # 매수 신호 확인
    if latest_data['Buy_Signal']:
        # 매수 신호가 True일 경우
        message = f"매수 신호 발생: 날짜 {latest_data.name}, 종가 {latest_data['Close']}"
        # send_email 함수 또는 send_fcm_message 함수 호출
        send_email("매수 신호 발생", message, receiver_email, dotenv_path)
        send_telegram(message, dotenv_path)

    # 매도 신호 확인
    elif latest_data['Sell_Signal']:
        # 매도 신호가 True일 경우
        message = f"매도 신호 발생: 날짜 {latest_data.name}, 종가 {latest_data['Close']}"
        # send_email 함수 또는 send_fcm_message 함수 호출
        send_email("매도 신호 발생", message, receiver_email, dotenv_path)
        send_telegram(message, dotenv_path)
