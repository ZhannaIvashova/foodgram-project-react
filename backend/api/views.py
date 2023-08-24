from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, viewsets, status
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import (
    AdminOrAuthorOrReadOnly, UserOrAdminOrReadOnly
)
from api.serializers import (
    ChangePasswordSerializer, FavoriteSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeSerializer, ShoppingCartSerializer,
    SubscribeCreateSerializer, SubscribeReadSerializer,
    TagSerializer, UserCreateSerializer, UserReadSerializer
)
from foodgram.settings import (
    DOWNLOAD, SET_PASSWORD, SUBSCRIPTIONS, USER_ME
)
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag
)
from users.models import Subscribe

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    permission_classes = (UserOrAdminOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', 'username')

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от типа запроса."""
        if self.request.method == 'GET' or self.request.method == 'PATCH':
            return UserReadSerializer
        return UserCreateSerializer

    @action(
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        url_path=USER_ME,
        detail=False,
    )
    def get_me(self, request):
        """Определяет сериализатор для просмотра текущего пользователя."""
        user = request.user
        serializer = UserReadSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=('POST',),
        permission_classes=(IsAuthenticated,),
        url_path=SET_PASSWORD,
        detail=False,
    )
    def change_password(self, request):
        """Определяет сериализатор для смены пароля и
               изменяет его в базе данных."""
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Пароль успешно изменен'})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        url_path=SUBSCRIPTIONS,
        detail=False,
    )
    def get_subscriptions(self, request):
        """Определяет сериализатор для просмотра подписок."""
        user = self.request.user
        user_obj = user.subscriber.all()
        author_id = [obj.author_id for obj in user_obj]
        author_obj = User.objects.filter(id__in=author_id)

        page = self.paginate_queryset(author_obj)

        serializer = SubscribeReadSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """Вьюсет для создания/удаления подписок ."""
    serializer_class = SubscribeCreateSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author'] = get_object_or_404(
            User, id=self.kwargs.get('user_id'))
        return context

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))
        serializer.save(user=self.request.user, author=author)

    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        if user.subscriber.filter(author=user_id).exists():
            subscription = Subscribe.objects.get(user=user, author=author)
            subscription.delete()
        else:
            return Response(
                {'detail': 'Вы не подписаны на данного пользователя'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {'detail': 'Успешная отписка'},
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (AdminOrAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от типа запроса."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        url_path=DOWNLOAD,
        detail=False,
    )
    def get_shopping_cart(self, request):
        """Скачивание списка покупок."""
        user = self.request.user
        user_obj = user.shopping_cart.all()
        recipes_id = [obj.recipe_id for obj in user_obj]
        recipes = IngredientRecipe.objects.filter(recipe_id__in=recipes_id)
        recipes_dict = {}
        for recipe in recipes:
            ingredient = recipe.ingredient
            amount = recipe.amount

            if ingredient.id in recipes_dict:
                recipes_dict[ingredient.id] += amount
            else:
                recipes_dict[ingredient.id] = amount

        shop_list = ['Ваш список покупок:\n']
        for number, (ingredient, amount) in enumerate(recipes_dict.items(),
                                                      start=1):
            ingredient = Ingredient.objects.get(id=ingredient)
            shop_list += (
                f'{number}) {ingredient.name} ({ingredient.measurement_unit})'
                f'- {amount}\n'
            )

        response = HttpResponse(shop_list, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt'
        )
        return response


class FavoriteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Вьюсет для создания/удаления избранного."""
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe'] = get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id'))
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if user.favorite.filter(recipe=recipe_id).exists():
            favorite = Favorite.objects.get(user=user, recipe=recipe)
            favorite.delete()
        else:
            return Response(
                {'detail': 'Рецепт не был добавлен в избранное'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """Вьюсет для создания/удаления покупок."""
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe'] = get_object_or_404(
            Recipe, id=self.kwargs.get('recipe_id'))
        return context

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if user.shopping_cart.filter(recipe=recipe_id).exists():
            shopping_cart = ShoppingCart.objects.get(user=user, recipe=recipe)
            shopping_cart.delete()
        else:
            return Response(
                {'detail': 'Рецепт не был добавлен в список покупок'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
