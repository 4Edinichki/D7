from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string  # импортируем функцию, которая срендерит наш html
from .models import PostCategory, Post, Category, User
from django.conf import settings


@receiver(m2m_changed, sender=Post.category_news.through)
def notify_new_post(sender, instance, **kwargs):
    change_category = Category.objects.filter(postcategory__post=instance)
    if change_category.count() == 1:
        category = Category.objects.get(postcategory__post=instance)

        subscribers = User.objects.filter(categorysubscribers__category=category)
        email_subscribers = []
        for email in subscribers:
            email_subscribers.append(email.email)

        new_post = f'{instance.title}'
        # link_id = instance.id
        # link = f'http://127.0.0.1:8000/news/{link_id}'
        # html_content = render_to_string('new_content.html',
        #                                 {
        #                                     'new_post': new_post, 'link': link
        #                                 })
        msg = EmailMultiAlternatives(
            subject=f'New posts in category you have subscribed to',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=email_subscribers,
        )
        # msg.attach_alternative(html_content, "text/html")
        msg.send()
