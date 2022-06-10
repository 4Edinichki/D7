from django.apps import AppConfig

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # from .tasks import send_mails
        from .scheduler import appointment_scheduler
        appointment_scheduler.add_job(
            id='send_mails',
            func=lambda: print('123'),
            trigger='interval',
            seconds=10,
        )
        appointment_scheduler.start()
