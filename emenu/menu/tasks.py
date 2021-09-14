from datetime import datetime, timedelta, date
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.utils import timezone
from emenu.menu.models import Dish


def get_new_dishes_mail_contents():
    """
    Prepare emails that notify users of yesterday's changes to dishes.
    Returns a list of tuples (user_email, mail_content) to send.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    newly_added_dishes = Dish.objects.filter(date_added__gte=yesterday,
                                             date_added__lt=today)
    newly_modified_dishes = Dish.objects.filter(date_modified__gte=yesterday,
                                                date_modified__lt=today).exclude(id__in=newly_added_dishes)

    if newly_added_dishes.count() + newly_modified_dishes.count() == 0:
        # No updates.
        return []

    results = []
    for user in User.objects.all():
        user_greeting_name = user.first_name
        if user_greeting_name == "":
            user_greeting_name = user.username

        message = render_to_string('menu/new-dishes-mail.html', context={
            'newly_added_dishes': newly_added_dishes,
            'newly_modified_dishes': newly_modified_dishes,
            'user_greeting_name': user_greeting_name,
        })
        results.append((user.email, message))
    return results


@shared_task
def schedule_new_dishes_mail():
    mail_subject = 'eMenu - Dish updates'
    emails_and_contents = get_new_dishes_mail_contents()
    for user_email, message in emails_and_contents:
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.content_subtype = 'html'
        email.send()
