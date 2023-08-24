import base64

import webcolors
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from djoser.serializers import (PasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from foodgram.settings import RECIPES_LIMIT
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe

from rest_framework import serializers


User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователей."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserReadSerializer(UserSerializer):
    """Сериализатор для просмотра пользователей."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            is_subscribed = user.subscriber.filter(author=obj.id).exists()
        else:
            is_subscribed = False

        return is_subscribed


class ChangePasswordSerializer(PasswordSerializer):
    """Сериализатор для смены пароля."""

    current_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context.get('request').user
        if check_password(data.get('current_password'), user.password):
            if data.get('current_password') == data.get('new_password'):
                raise serializers.ValidationError(
                    'Пароли не могут быть оинаковыми')
        else:
            raise serializers.ValidationError('Ведите корректный пароль')

        try:
            validate_password(data.get('new_password'), user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)})

        return data


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода поля 'recipes' в просмотре подписок,
       вывод избранных рецептов и покупок."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра подписок."""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        is_subscribed = user.subscriber.filter(author=obj.id).exists()
        return is_subscribed

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:RECIPES_LIMIT]
        serializer = RecipeListSerializer(
            recipes,
            many=True,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = obj.recipes.all()
        return recipes.count()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    author = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Subscribe
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        author = self.context.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Пользователь не может подписаться сам на себя')

        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError('Подписка уже существует')
        return data

    def to_representation(self, instance):
        serializer = SubscribeReadSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и ингредиентов (чтение)."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецептов и ингредиентов
        (создание/редактирование/удаление)."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(validators=(MinValueValidator(1),),)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов (GET- запросы)."""

    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_shopping_cart'
    )
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = UserReadSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'ingredients',
            'tags',
            'cooking_time',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipeReadSerializer(
            IngredientRecipe.objects.filter(recipe=obj).all(), many=True
        )
        return ingredients.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            is_favorited = user.favorite.filter(recipe=obj).exists()
        else:
            is_favorited = False

        return is_favorited

    def get_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            shopping_cart = user.shopping_cart.filter(recipe=obj).exists()
        else:
            shopping_cart = False

        return shopping_cart


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования/удаления рецептов."""

    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'image',
            'ingredients',
            'tags',
            'cooking_time',
            'author'
        )
        read_only_fields = ('author',)

    def validate_ingredients(self, data):
        ingredients_list = []
        ingredients_data = self.initial_data.get('ingredients')
        ingredients = Ingredient.objects.all()
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')

            if ingredient_id in ingredients_list:
                ingredient_name = ingredients.filter(id=ingredient_id).first()
                raise serializers.ValidationError(
                    f'Вы уже выбрали ингредиент: {ingredient_name}')
            ingredients_list.append(ingredient_id)

            if not ingredients.filter(id=ingredient_id).first():
                raise serializers.ValidationError(
                    'Несуществующий ингредиент, '
                    'выбирете ингредиент из предустановленного списка')

        if not ingredients_list:
            raise serializers.ValidationError('Задайте ингредиент')
        return data

    def validate_tags(self, data):
        tags_list = []
        tags_data = self.initial_data.get('tags')
        tags = Tag.objects.all()
        for tag_id in tags_data:
            if tag_id in tags_list:
                tag_name = tags.filter(id=tag_id).first()
                raise serializers.ValidationError(
                    f'Вы уже выбрали тег: {tag_name}')
            tags_list.append(tag_id)

        if not tags_list:
            raise serializers.ValidationError('Задайте тег')
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredient_data = validated_data.pop('ingredients')
        tag_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tag_data)

        for ingredient in ingredient_data:
            amount = ingredient.get('amount')
            ingredient_obj = Ingredient.objects.get(
                id=ingredient.get('id')
            )
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient_obj, amount=amount)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if 'ingredients' in validated_data:
            ingredient_data = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingredient in ingredient_data:
                amount = ingredient.get('amount')
                ingredient_obj = Ingredient.objects.get(
                    id=ingredient.get('id'))
                IngredientRecipe.objects.create(
                    recipe=instance, ingredient=ingredient_obj, amount=amount)

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        recipe = self.context.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')
        return data

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для покупок."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        user = data.get('user')
        recipe = self.context.get('recipe')
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок')
        return data

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        )
        return serializer.data
