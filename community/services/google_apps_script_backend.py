import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class GoogleAppsScriptEmailBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)

        self.url = getattr(settings, "GOOGLE_APPS_SCRIPT_EMAIL_URL", "")
        self.secret = getattr(settings, "GOOGLE_APPS_SCRIPT_EMAIL_SECRET", "")

        if not self.url or not self.secret:
            raise ImproperlyConfigured(
                "Google Apps Script email URL or secret is missing."
            )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0

        for message in email_messages:
            try:
                recipients = message.recipients()

                if not recipients:
                    continue

                html_body = ""

                for content, mimetype in getattr(message, "alternatives", []):
                    if mimetype == "text/html":
                        html_body = str(content)
                        break

                # Apps Script accepts one recipient per request.
                for recipient in recipients:
                    payload = {
                        "secret": self.secret,
                        "to": recipient,
                        "subject": message.subject or "",
                        "body": message.body or "",
                        "html_body": html_body,
                    }

                    request_data = json.dumps(payload).encode("utf-8")

                    request = urllib.request.Request(
                        self.url,
                        data=request_data,
                        headers={
                            "Content-Type": "application/json",
                        },
                        method="POST",
                    )

                    # urllib follows Google's ContentService redirect.
                    with urllib.request.urlopen(request, timeout=30) as response:
                        result = json.loads(
                            response.read().decode("utf-8")
                        )

                    if not result.get("success"):
                        service_error = result.get("error", "Unknown Google Apps Script error")

                        raise RuntimeError(
                            f"Google Apps Script rejected the request: {service_error}"
                        )

                sent_count += 1

            except Exception as error:
                logger.error(
                    "Google Apps Script email failed: %s",
                    str(error)[:500],
                )

                if not self.fail_silently:
                    raise

        return sent_count