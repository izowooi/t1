# Trend Follower
import yfinance as yf
from SendEmail import send_email
from SendTelegram import send_telegram
import requests
from datetime import datetime
import pandas as pd


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


def str_to_bool(s):
    return s.lower() in ('true', '1', 't', 'y', 'yes')


def data_from_yahoo(ticker):
    print(f'매매 신호 확인: {ticker}')
    data = yf.download(ticker, start='2020-01-01')

    return data

#364980
def data_from_naver(ticker):
    current_date = datetime.now()
    end_date = current_date.strftime('%Y%m%d')
    start_date = '20200101'
    print(f'매매 신호 확인: {ticker}')
    print(f'end_date : {end_date}')
    url = f"https://api.finance.naver.com/siseJson.naver?symbol={ticker}&requestType=1&startTime={start_date}&endTime={end_date}&timeframe=day"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None

    data = response.text

    data = data.replace('\n', '').replace('\t', '').replace(' ', '')
    data = data.replace('날짜', 'Date')
    data = data.replace('시가', 'Open')
    data = data.replace('고가', 'High')
    data = data.replace('저가', 'Low')
    data = data.replace('종가', 'Close')
    data = data.replace('거래량', 'Volume')
    data = data.replace('외국인소진율', 'Foreigner')

    data = eval(data)

    data = pd.DataFrame(data[1:], columns=data[0])

    return data


def send_trading_signal_alert(ticker, dotenv_path='.env', is_yahoo=True, test_buy_signal=False):
    if is_yahoo:
        data = data_from_yahoo(ticker)
    else:
        data = data_from_naver(ticker)

    if data is None:
        Exception('데이터를 가져오지 못했습니다.')
        return
    # 이동 평균 계산
    data = calculate_moving_averages(data, short_window=5, long_window=60)

    # 매매 신호 생성
    data = generate_signals(data)

    # 결과 확인
    print(data[['Close', 'Short_MA', 'Long_MA', 'Buy_Signal', 'Sell_Signal']].tail(n=60))

    # 결과 확인 및 알림 전송
    latest_data = data.iloc[-1]# 가장 최근 데이터
    print('\n')
    print(latest_data)

    receiver_email = 'izowooi85@gmail.com'

    if test_buy_signal:
        latest_data['Buy_Signal'] = True

    print(f'dotenv_path의 값: {dotenv_path}')

    # 매수 신호가 True일 경우
    if latest_data['Buy_Signal']:
        message = f"[{ticker}] 매수 신호 발생: 날짜 {latest_data.name}, 종가 {latest_data['Close']}"
        send_email("매수 신호 발생", message, receiver_email, dotenv_path)
        send_telegram(message, dotenv_path)

    # 매도 신호가 True일 경우
    elif latest_data['Sell_Signal']:
        message = f"[{ticker}] 매도 신호 발생: 날짜 {latest_data.name}, 종가 {latest_data['Close']}"
        send_email("매도 신호 발생", message, receiver_email, dotenv_path)
        send_telegram(message, dotenv_path)
