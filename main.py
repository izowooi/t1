import os
from SendTradingSignal import send_trading_signal_alert


def main():
    ticker_list_str = os.getenv('ticker_list', 'MSFT')
    dotenv_path = os.getenv('dotenv_path', '.env')
    print(f'ticker_list_str의 값: {ticker_list_str}')
    print(f'dotenv_path의 값: {dotenv_path}')
    ticker_list = ticker_list_str.split(',')

    # 리스트의 각 요소에 대해 반복문을 실행합니다.
    for ticker in ticker_list:
        send_trading_signal_alert(ticker)




main()
