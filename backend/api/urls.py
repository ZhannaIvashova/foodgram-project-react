from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from api.views import (
    FavoriteViewSet, IngredientViewSet, RecipeViewSet,
    ShoppingCartViewSet, SubscribeViewSet, TagViewSet, UserViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteViewSet, basename='favorite')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shopping_cart')
router.register(r'users', UserViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='subscribe')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
