import sys
from SendTradingSignal import send_trading_signal_alert


def str_to_bool(s):
    return s.lower() in ('true', '1', 't', 'y', 'yes')


def main():
    # 커맨드 라인 인자를 가져옵니다.
    ticker_list_str = sys.argv[1] if len(sys.argv) > 1 else 'MSFT'
    dotenv_path = sys.argv[2] if len(sys.argv) > 2 else '.env'
    test_buy_signal = str_to_bool(sys.argv[3]) if len(sys.argv) > 3 else False
    is_yahoo = str_to_bool(sys.argv[4]) if len(sys.argv) > 4 else False

    print(f'ticker_list_str : {ticker_list_str}')
    print(f'dotenv_path : {dotenv_path}')
    print(f'test_buy_signal : {test_buy_signal}')
    print(f'is_yahoo : {is_yahoo}')
    ticker_list = ticker_list_str.split(',')

    for ticker in ticker_list:
        send_trading_signal_alert(ticker, dotenv_path, is_yahoo, test_buy_signal)


main()
