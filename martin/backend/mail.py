"""SMTP email helpers for martin.backend."""

from dataclasses import dataclass, field
from email.message import EmailMessage as _EmailMessage
import smtplib


@dataclass
class SMTPConfig:
    host: str
    port: int = 587
    username: str = ""
    password: str = ""
    sender: str = ""
    sender_name: str = ""
    use_tls: bool = True
    use_ssl: bool = False
    timeout: float = 10.0

    @classmethod
    def from_env(cls, prefix="MARTIN_SMTP_"):
        import os

        return cls(
            host=os.getenv(prefix + "HOST", ""),
            port=int(os.getenv(prefix + "PORT", "587")),
            username=os.getenv(prefix + "USERNAME", ""),
            password=os.getenv(prefix + "PASSWORD", ""),
            sender=os.getenv(prefix + "SENDER", ""),
            sender_name=os.getenv(prefix + "SENDER_NAME", ""),
            use_tls=os.getenv(prefix + "USE_TLS", "1").lower() not in {"0", "false", "no"},
            use_ssl=os.getenv(prefix + "USE_SSL", "0").lower() in {"1", "true", "yes"},
            timeout=float(os.getenv(prefix + "TIMEOUT", "10")),
        )


@dataclass
class MailMessage:
    subject: str
    to: list[str] = field(default_factory=list)
    text: str = ""
    html: str = ""
    sender: str = ""
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    reply_to: str = ""


class Mailer:
    """Cliente SMTP sencillo para martin.backend."""

    def __init__(self, config: SMTPConfig):
        self.config = config

    def send(
        self,
        subject,
        to,
        text="",
        html="",
        sender=None,
        cc=None,
        bcc=None,
        reply_to=None,
    ):
        message = MailMessage(
            subject=subject,
            to=self._coerce_recipients(to),
            text=text,
            html=html,
            sender=sender or "",
            cc=self._coerce_recipients(cc),
            bcc=self._coerce_recipients(bcc),
            reply_to=reply_to or "",
        )
        return self.send_message(message)

    def send_message(self, message: MailMessage):
        cfg = self.config
        sender = message.sender or self._default_sender()
        if not sender:
            raise ValueError("SMTP sender is required")
        recipients = message.to + message.cc + message.bcc
        if not recipients:
            raise ValueError("At least one recipient is required")
        if not message.text and not message.html:
            raise ValueError("Email requires text or html content")

        email_msg = _EmailMessage()
        email_msg["Subject"] = message.subject
        email_msg["From"] = sender
        email_msg["To"] = ", ".join(message.to)
        if message.cc:
            email_msg["Cc"] = ", ".join(message.cc)
        if message.reply_to:
            email_msg["Reply-To"] = message.reply_to

        if message.html and message.text:
            email_msg.set_content(message.text)
            email_msg.add_alternative(message.html, subtype="html")
        elif message.html:
            email_msg.set_content(self._html_to_text(message.html))
            email_msg.add_alternative(message.html, subtype="html")
        else:
            email_msg.set_content(message.text)

        client = self._smtp_client()
        try:
            client.send_message(email_msg, from_addr=sender, to_addrs=recipients)
        finally:
            try:
                client.quit()
            except Exception:
                pass
        return {
            "ok": True,
            "to": recipients,
            "subject": message.subject,
        }

    def _smtp_client(self):
        cfg = self.config
        if cfg.use_ssl:
            client = smtplib.SMTP_SSL(cfg.host, cfg.port, timeout=cfg.timeout)
        else:
            client = smtplib.SMTP(cfg.host, cfg.port, timeout=cfg.timeout)
        if not cfg.use_ssl and cfg.use_tls:
            client.starttls()
        if cfg.username:
            client.login(cfg.username, cfg.password)
        return client

    def _default_sender(self):
        cfg = self.config
        if cfg.sender_name and cfg.sender:
            return f"{cfg.sender_name} <{cfg.sender}>"
        return cfg.sender

    def _coerce_recipients(self, value):
        if not value:
            return []
        if isinstance(value, str):
            return [value]
        return [str(item) for item in value if item]

    def _html_to_text(self, html):
        import re

        text = re.sub(r"<br\\s*/?>", "\n", html, flags=re.I)
        text = re.sub(r"</p\\s*>", "\n\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()
