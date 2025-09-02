import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText


def send_email(subject, content, recipient, dot_env_path='.env'):
    load_dotenv(dot_env_path)

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'izowooi85@gmail.com'
    sender_password = os.getenv('EMAIL_PASSWORD')#비밀번호 가져오기

    # SMTP 서버 연결 및 로그인
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(sender_email, sender_password)

    # 이메일 메시지 생성
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient

    # 이메일 전송
    smtp.sendmail(sender_email, recipient, msg.as_string())
    smtp.quit()


#send_email('sub', 'con', 'izowooi85@gmail.com')
