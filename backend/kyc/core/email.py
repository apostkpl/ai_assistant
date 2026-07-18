import logging
import smtplib
from email.message import EmailMessage

from kyc.config.settings import settings

logger = logging.getLogger(__name__)

def send_verification_email(to_email: str, token: str) -> None:
    """
    Constructs and sends an HTML verification email via SMTP.
    """
    logger.debug(f"Preparing verification email for {to_email}")

    # 1. Build the verification URL
    verify_url = f"http://localhost:8000/auth/verify-email?token={token}" # No domain yet

    # 2. Construct the core message
    msg = EmailMessage()
    msg['Subject'] = "Please verify your email address"
    msg['From'] = f"{settings.email.from_name} <{settings.email.from_email}>"
    msg['To'] = to_email

    # 3. Attach the HTML payload
    html_content = f"""\
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Welcome to My App</h2>
            <p>Thank you for registering. To complete your setup and activate your account, please verify your email address.</p>
            <div style="margin: 20px 0;">
                <a href="{verify_url}"
                   style="background-color: #007BFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                   Verify Email
                </a>
            </div>
            <p style="font-size: 0.9em; color: #666;">
                Or paste this link into your browser:<br>
                <a href="{verify_url}">{verify_url}</a>
            </p>
        </body>
    </html>
    """
    msg.set_content(html_content, subtype='html')

    # 4. Transmit via standard SMTP connection
    try:
        # Connect to the SMTP server
        with smtplib.SMTP(settings.email.smtp_host, settings.email.smtp_port) as server:
            # Upgrade the connection to a secure TLS tunnel
            server.starttls()

            # Authenticate using your credentials
            server.login(settings.email.smtp_username, settings.email.smtp_password)

            # Dispatch the payload
            server.send_message(msg)

        logger.info(f"Verification email successfully transmitted to {to_email}")

    except Exception as e:
        logger.error(f"SMTP transmission failed for {to_email}: {str(e)}", exc_info=True)
