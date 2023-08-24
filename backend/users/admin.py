from django.contrib import admin
from django.contrib.auth import get_user_model
from users.models import Subscribe

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка админки для пользователей."""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author'
    )
    search_fields = ('pk', 'user')
    empty_value_display = '-пусто-'
