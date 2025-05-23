import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from datetime import datetime

EMAIL_USER = "tp869252@gmail.com"
EMAIL_PASS = "dlce zmty zrwt kifv"

TELEGRAM_BOT_TOKEN = "7363170467:AAGuv6mXsijDFXgqIbPuCJyqcuGBqsnqyZ0"
ZALO_API_URL = "http://localhost:8080/api/sendNotification"


style = """
<style>
    body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
    .email-container { max-width: 600px; margin: auto; background: #fff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
    .email-header { background-color: #0073e6; color: white; padding: 20px; text-align: center; font-size: 24px; }
    .email-body { padding: 20px; font-size: 16px; color: #333; }
    .cta-button { display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; margin-top: 20px; text-decoration: none; }
    .footer { background-color: #f1f1f1; text-align: center; padding: 10px; font-size: 14px; color: #888; }
</style>
"""

def content_login(ip, link):
    return f"""
        Chúng tôi đã nhận được yêu cầu đăng nhập vào tài khoản của bạn từ địa chỉ IP <strong>{ip}</strong>.<br><br>
        Nếu bạn không thực hiện, vui lòng nhấn nút dưới để bảo vệ tài khoản:<br>
        <a href="{link}" class="cta-button">Bảo vệ tài khoản</a>
    """

def content_change_password(link):
    return f"""
        Yêu cầu thay đổi mật khẩu của bạn được ghi nhận.<br><br>
        Nếu không phải bạn, hãy liên hệ hỗ trợ. Nếu đúng, nhấn:<br>
        <a href="{link}" class="cta-button">Đổi mật khẩu</a>
    """

def content_otp(otp):
    return f"""
        Để xác thực tài khoản, sử dụng mã OTP:<br><br>
        <div style="font-size: 20px; color: #e74c3c;">{otp}</div><br>
        Mã có hiệu lực 10 phút.
    """

def send_email(to, type_, data):
    subject = ""
    body_content = ""
    if type_ == "login":
        subject = "Thông báo về Đăng nhập tài khoản"
        body_content = content_login(data["ip"], data["url"])
    elif type_ == "changePassword":
        subject = "Thông báo về Đổi mật khẩu"
        body_content = content_change_password(data["url"])
    elif type_ == "otp":
        subject = "Mã OTP xác thực tài khoản"
        body_content = content_otp(data["code"])

    html = f"""
    <html>
    <head>{style}</head>
    <body>
        <div class="email-container">
            <div class="email-header">{subject}</div>
            <div class="email-body">
                <p><strong>Kính gửi quý khách,</strong></p>
                <p>{body_content}</p>
            </div>
            <div class="footer">© 2024 Hệ thống Quản lý Tài khoản</div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f'Document Repository <{EMAIL_USER}>'
    msg['To'] = to
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to, msg.as_string())
        print("Email sent successfully.")
        return True
    except Exception as e:
        print("Failed to send email:", str(e))
        return False

# ------------------- TELEGRAM -------------------

def get_telegram_message(type_, data):
    time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    if type_ == "login":
        return f"""<b>Thông báo Đăng nhập</b>\nTài khoản đăng nhập lúc <i>{time}</i> từ IP <i>{data['ip']}</i>."""
    elif type_ == "changePassword":
        return f"""<b>Thông báo Đổi mật khẩu</b>\nMật khẩu thay đổi lúc <i>{time}</i>."""
    elif type_ == "otp":
        return f"""<b>Mã OTP:</b> <pre>{data['code']}</pre>\nHiệu lực 5 phút."""

def send_telegram_message(chat_id, type_, data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": get_telegram_message(type_, data),
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print("Lỗi gửi Telegram:", e)
        return False

# ------------------- ZALO -------------------

def get_zalo_message(type_, data):
    time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    if type_ == "login":
        return f"Đăng nhập lúc {time} từ IP {data['ip']}."
    elif type_ == "changePassword":
        return f"Mật khẩu đã thay đổi lúc {time}."
    elif type_ == "otp":
        return f"Mã OTP: {data['code']} (hiệu lực 5 phút)."

def send_zalo(uid, type_, data):
    payload = {
        "uid": uid,
        "content": get_zalo_message(type_, data)
    }
    try:
        response = requests.post(ZALO_API_URL, json=payload)
        return response.json().get("status", False)
    except Exception as e:
        print("Lỗi gửi Zalo:", e)
        return False
