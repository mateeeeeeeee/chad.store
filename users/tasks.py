from celery import shared_task

from django.core.mail import send_mail

@shared_task
def send_mail_async(subject,message,recipient_email):
    send_mail(subject, message, "ragaca@example.com", [recipient_email])