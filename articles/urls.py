from django.urls import path
from .views import ArticleListCreateView
from .views import ArticleRetrieveUpdateDestroyView
from .user_views import UserListCreateView, UserRetrieveUpdateDestroyView

urlpatterns = [
    path('', ArticleListCreateView.as_view(), name='article-list-create'),
    path('<int:pk>/', ArticleRetrieveUpdateDestroyView.as_view(), name='article-detail'),
    # User management endpoints (admin only)
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
]
