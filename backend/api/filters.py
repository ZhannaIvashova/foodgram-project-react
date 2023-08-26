from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр выборки рецепта по избранному, автору, списку покупок и тегам."""

    author = filters.CharFilter(
        field_name='author'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none()

        recipes_id = user.favorite.filter(user=user).values_list(
            'recipe', flat=True)
        return queryset.filter(id__in=recipes_id) if value else queryset.all()

    def get_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none()

        recipes_id = user.shopping_cart.filter(user=user).values_list(
            'recipe', flat=True)
        return queryset.filter(id__in=recipes_id) if value else queryset.all()


class IngredientFilter(filters.FilterSet):
    """Фильтр выборки ингредиента."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
