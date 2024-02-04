import json
import datetime


def load_sent_log(log_path="ticker_alerts_history.json"):
    try:
        with open(log_path, "r") as file:
            sent_logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        sent_logs = {}
    return sent_logs


def update_sent_log(ticker, log_path="ticker_alerts_history.json"):
    sent_logs = load_sent_log(log_path)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if ticker in sent_logs:
        if today not in sent_logs[ticker]:
            sent_logs[ticker].append(today)
    else:
        sent_logs[ticker] = [today]

    with open(log_path, "w") as file:
        json.dump(sent_logs, file, indent=4)


# 이미 보낸 경우는 True 를 반환합니다.
def has_already_sent(ticker, log_path="ticker_alerts_history.json"):
    sent_logs = load_sent_log(log_path)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return ticker in sent_logs and today in sent_logs[ticker]
