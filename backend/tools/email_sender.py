import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config.settings import settings


class EmailSenderTool:

    def __init__(self):
        self.gmail   = settings.GMAIL_ADDRESS
        self.app_pwd = settings.GMAIL_APP_PASSWORD
        self.enabled = bool(self.gmail and self.app_pwd)

    def send(self, to_email: str, subject: str, body: str) -> dict:
        if not self.enabled:
            # Mock send — log but don't actually send
            return {
                "status":  "mock_sent",
                "to":      to_email,
                "subject": subject,
                "message": "Gmail not configured — email logged but not sent",
            }
        try:
            msg = MIMEMultipart("alternative")
            msg["From"]    = self.gmail
            msg["To"]      = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.gmail, self.app_pwd)
                server.sendmail(self.gmail, to_email, msg.as_string())

            return {"status": "sent", "to": to_email, "subject": subject}

        except Exception as e:
            return {"status": "failed", "error": str(e), "to": to_email}