from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe,
    ShoppingCart, Tag, TagRecipe
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки админ-панели ингредиентов."""

    empty_value_display = '-отсутствует-'
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки админ-панели тегов."""

    empty_value_display = '-отсутствует-'
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки админ-панели рецептов."""

    empty_value_display = '-отсутствует-'
    list_display = (
        'pk',
        'name',
        'text',
        'cooking_time',
        'author',
        'is_favorited',
        'pub_date'
    )
    list_filter = ('name', 'tags__name', 'author__username')
    search_fields = ('name', 'tags__name', 'author__username')

    def is_favorited(self, obj):
        favorite_count = obj.favorite.count()
        return favorite_count

    is_favorited.short_description = 'Добавлен в избранное (кол.раз)'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Настройки соответствия рецептов и ингредиентов."""

    empty_value_display = '-отсутствует-'
    list_display = (
        'pk',
        'ingredient',
        'recipe',
        'amount'
    )
    list_filter = ('ingredient', 'recipe')
    search_fields = ('ingredient', 'recipe')


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    """Настройки соответствия рецептов и тегов."""

    empty_value_display = '-отсутствует-'
    list_display = (
        'pk',
        'tag',
        'recipe'
    )
    list_filter = ('tag', 'recipe')
    search_fields = ('tag', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    search_fields = ('pk', 'user')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe'
    )
    search_fields = ('pk', 'user')
    empty_value_display = '-пусто-'
