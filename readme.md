## 설명
추세 매매 전략 중 하나인 5-60일 이동평균선을 이용한 매매 전략을 구현한 프로그램입니다.
현재 나스닥만 가능하며, 매도/매수 규칙에 따라 이메일과 텔레그램 메시지를 전송합니다.

## 실행방법
```
TICKER_LIST="MSFT,AMZN,NFLX,TMF,TMV,GOOGL"
#TICKER_LIST="GOOGL"
DOTENV_PATH="/var/lib/jenkins/auth/.env"
TEST_BUY_SIGNAL=False

python3 ./main.py $TICKER_LIST $DOTENV_PATH $TEST_BUY_SIGNAL
```

## 준비할 것
- .env 파일 생성
- .env 파일에 아래 내용 추가
```
EMAIL_PASSWORD=EMAIL_PASSWORD
TELEGRAM_TOKEN=TELEGRAM_TOKEN
TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID
```

## 키값에 대한 설명
- EMAIL_PASSWORD: 구글 이메일 앱 패스워드 ([링크](https://support.google.com/mail/answer/185833))
- TELEGRAM_TOKEN: 텔레그램 봇 토큰 ([링크](https://ykarma1996.tistory.com/107))
- TELEGRAM_CHAT_ID: 텔레그램 채팅방 ID ([링크](https://gabrielkim.tistory.com/entry/Telegram-Bot-Token-%EB%B0%8F-Chat-Id-%EC%96%BB%EA%B8%B0))

## 설치한 패키지명
- yfinance
- python-dotenv
- python-telegram-bot
