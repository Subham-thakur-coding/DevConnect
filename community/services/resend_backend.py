import logging
import os

import resend

from django.core.mail.backends.base import BaseEmailBackend


logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Django email backend using the Resend HTTP API.

    Supports plain-text and HTML email messages.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)

        self.api_key = os.getenv("RESEND_API_KEY")

        self.from_email = os.getenv("DEFAULT_FROM_EMAIL", "").strip()

        if not self.api_key:
            raise RuntimeError(
                "RESEND_API_KEY is missing from environment variables."
            )

        if not self.from_email:
            raise RuntimeError(
                "DEFAULT_FROM_EMAIL is missing from environment variables."
            )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        resend.api_key = self.api_key

        sent_count = 0

        for message in email_messages:
            try:
                if not message.recipients():
                    continue

                params = {
                    "from": message.from_email or self.from_email,
                    "to": message.recipients(),
                    "subject": message.subject or "",
                    "text": message.body or "",
                }

                # Preserve HTML alternatives when present.
                for alternative, mimetype in message.alternatives:
                    if mimetype == "text/html":
                        params["html"] = alternative
                        break

                # Send through Resend's HTTPS API.
                result = resend.Emails.send(params)

                logger.info(
                    "Resend accepted an email. Response: %s",
                    result,
                )

                sent_count += 1

            except Exception:
                logger.exception(
                    "Resend email delivery failed for recipient(s): %s",
                    message.recipients(),
                )

                if not self.fail_silently:
                    raise

        return sent_count