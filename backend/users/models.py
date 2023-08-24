from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Переопределяем модель пользователей."""

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин'
    )
    email = models.EmailField(
        max_length=254,
        null=False,
        unique=True,
        blank=False,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        null=False,
        blank=False,
        verbose_name='Фамилия пользователя'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь (подписчик)'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор рецепта'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
