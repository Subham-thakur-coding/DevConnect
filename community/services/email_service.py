import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


def send_devconnect_email(
    subject,
    recipient,
    template_name,
    context=None,
):
    """
    Send a branded DevConnect HTML email.

    Email failures are logged and do not interrupt
    the main website functionality.
    """

    if not recipient:
        logger.warning(
            "DevConnect email skipped: recipient email is missing."
        )
        return False

    context = context or {}

    context.setdefault(
        "site_name",
        "DevConnect",
    )

    context.setdefault(
        "site_url",
        getattr(settings, "SITE_URL", ""),
    )

    try:
        text_content = render_to_string(
            f"emails/{template_name}.txt",
            context,
        )

        html_content = render_to_string(
            f"emails/{template_name}.html",
            context,
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )

        email.attach_alternative(
            html_content,
            "text/html",
        )

        email.send(fail_silently=False)

        logger.info(
            "DevConnect email sent successfully to %s",
            recipient,
        )

        return True

    except Exception:
        logger.exception(
            "Failed to send DevConnect email to %s",
            recipient,
        )

        return False