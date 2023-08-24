from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр выборки рецепта по избранному, автору, списку покупок и тегам."""

    CHOICES = (
        ('0', 'False'),
        ('1', 'True')
    )

    author = filters.CharFilter(
        field_name='author'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.ChoiceFilter(
        choices=CHOICES,
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.ChoiceFilter(
        choices=CHOICES,
        method='get_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            user_obj = user.favorite.all()
            recipes_id_list = [obj.recipe_id for obj in user_obj]
            return (
                queryset.filter(id__in=recipes_id_list) if value == '1' else
                queryset.exclude(id__in=recipes_id_list))
        else:
            return queryset.none()

    def get_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            user_obj = user.shopping_cart.all()
            recipes_id_list = [obj.recipe_id for obj in user_obj]
            return (
                queryset.filter(id__in=recipes_id_list) if value == '1' else
                queryset.exclude(id__in=recipes_id_list))
        else:
            return queryset.none()


class IngredientFilter(filters.FilterSet):
    """Фильтр выборки ингредиента."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
