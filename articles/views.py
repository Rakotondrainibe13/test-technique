from rest_framework import generics
from .models import Article
from .serializers import ArticleSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import ArticlePermission
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response

class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    permission_classes = [ArticlePermission]

    def list(self, request, *args, **kwargs):
        cache_key = f"articles_list:{request.query_params.get('status', 'all')}:{request.query_params.get('page', 1)}"
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)
        response = super().list(request, *args, **kwargs)
        # Cache TimeOut 1 minute for dynamic data
        cache.set(cache_key, response.data, timeout=60)
        return response

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ArticleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]
