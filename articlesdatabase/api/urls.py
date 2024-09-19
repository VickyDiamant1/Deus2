from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterUserAPIView, UserDetailAPI, ArticleViewSet, TagViewSet, UserListAPIView, CommentViewSet


router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('user/', UserDetailAPI.as_view(), name='user-detail'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('', include(router.urls)),
]