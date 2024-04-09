from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import AccountVerificationToken


def sendVerificationEmail(user_id, email: str):
    # send activation email token

    token: str = AccountVerificationToken.objects.get_or_create(
        user_id=user_id)[0]

    html_content = render_to_string(
        "verification-email.html", {"token": token})
    mail = EmailMessage(
        subject="Afroblend Account Verification",
        body=html_content,
        to=[email]
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=False)
