from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = "jeeves4service@gmail.com"
        self.password = "vzbcxdrqjeechohm"

    def send_email(self, to_address, subject, body):
        print(f"Sending email to {to_address} with subject '{subject}'...")
        msg = MIMEMultipart(body)
        msg['Subject'] = subject
        msg['From'] = "Jeeves@Service"
        msg['To'] = to_address

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, [to_address], msg.as_string())

        print(f"Email sent successfully to {to_address}")

if __name__ == "__main__":
    email_sender = EmailSender()
    email_sender.send_email("ambarish.vaidya@gmail.com", "Hello", "testing if this is working")