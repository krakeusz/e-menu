from datetime import datetime, timedelta, date
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.utils import timezone
from emenu.menu.models import Dish


@shared_task
def schedule_new_dishes_mail():
    today = date.today()
    yesterday = today - timedelta(days=1)
    newly_added_dishes = Dish.objects.filter(date_added__gte=yesterday,
                                             date_added__lt=today)
    newly_modified_dishes = Dish.objects.filter(date_modified__gte=yesterday,
                                                date_modified__lt=today).exclude(id__in=newly_added_dishes)

    if newly_added_dishes.count() + newly_modified_dishes.count() == 0:
        # No updates.
        return

    mail_subject = 'eMenu - Dish updates'

    for user in User.objects.all():
        user_greeting_name = user.first_name
        if user_greeting_name == "":
            user_greeting_name = user.username

        message = render_to_string('menu/new-dishes-mail.html', context={
            'newly_added_dishes': newly_added_dishes,
            'newly_modified_dishes': newly_modified_dishes,
            'user_greeting_name': user_greeting_name,
        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.content_subtype = 'html'
        email.send()

# docker run -d -p 5672:5672 rabbitmq
# celery -A emenu worker --loglevel=info -E -B
