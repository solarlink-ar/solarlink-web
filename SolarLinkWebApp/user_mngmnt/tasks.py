from django.core.mail import EmailMessage
from celery import shared_task

@shared_task()
def no_reply_sender(**kwargs):
    email = EmailMessage( kwargs["asunto"],
                          kwargs["mensaje"],
                          to=[kwargs["mail_to"]])
    email.send()