import random, smtplib

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(to_email, otp):
    # Sample using smtplib; replace with real credentials
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('YOUR_EMAIL@gmail.com', 'YOUR_APP_PASSWORD')
        smtp.sendmail('YOUR_EMAIL@gmail.com', to_email, f"Subject: Your OTP\nYour OTP is {otp}")
