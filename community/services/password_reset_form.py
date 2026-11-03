from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class DevConnectPasswordResetForm(PasswordResetForm):

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = render_to_string(
            subject_template_name,
            context
        ).strip()

        text_content = render_to_string(
            email_template_name,
            context
        )

        html_content = None

        if html_email_template_name:
            html_content = render_to_string(
                html_email_template_name,
                context
            )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email],
        )

        if html_content:
            email.attach_alternative(
                html_content,
                "text/html"
            )

        email.send()