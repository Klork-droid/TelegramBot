from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID польлзователя соц сети',
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
    )

    class Meta:
        verbose_name = 'Профиль'
