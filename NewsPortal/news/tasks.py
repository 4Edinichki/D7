from django.core.mail import mail_managers
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import localtime
from datetime import datetime, timedelta
from .models import Category, Post, User

import time


@shared_task
def mail_new_post(email_subscribers, new_post, link, category):
    msg = EmailMultiAlternatives(
        subject=f'New posts in category you have subscribed to',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email_subscribers,
    )
    msg.send()

@shared_task
def send_mail_subscribe(category, email):
    send_mail(
        subject='Hello',
        # имя клиента и дата записи будут в теме для удобства
        message=f'You are subscribed to the category {category}',  # сообщение с кратким описанием проблемы
        from_email=settings.DEFAULT_FROM_EMAIL,  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        recipient_list=[email,]  # здесь список получателей. Например, секретарь, сам врач и т. д.
    )

@shared_task
def send_mail_unsubscribe(category, email):
    send_mail(
        subject='Hello',
        # имя клиента и дата записи будут в теме для удобства
        message=f'You unsubscribed from the category {category}',  # сообщение с кратким описанием проблемы
        from_email=settings.DEFAULT_FROM_EMAIL,  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        recipient_list=[email]   # здесь список получателей. Например, секретарь, сам врач и т. д.
    )


@shared_task
def week_newsletter():
    print(f'Start{localtime()}')
    # Если день недели воскресенье
    if datetime.isoweekday(datetime.now()) == 1:
        # Высчитываем время 7 дней назад
        week = localtime() - timedelta(days=7)
        # По очереди берем каждую категорию, и делаем рассылку его подписчикам
        categories = Category.objects.all()
        for category in categories:
            # Берем всех подписчиков этой темы, и создаем список почтовых адресов
            subscribers = User.objects.filter(categorysubscribers__category=category)
            subscribers_emails = []
            for user in subscribers:
                subscribers_emails.append(user.email)
                # Достаем все новости этой категории за последние 7 дней
                post_list = Post.objects.filter(postcategory__category=category, date_create__gt=week)


                # HTML страница для мыло
                html_content = render_to_string('templates/weekly_newsletter.html',
                                                {'posts': post_list, 'category': category, })
                # Достаем
                # Собираем тело сообщения
                msg = EmailMultiAlternatives(
                    subject=f'All news for the last week',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=subscribers_emails,
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html
                msg.send()  # отсылаем
                print('Newsletter successfully sent')