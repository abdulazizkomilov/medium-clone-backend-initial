# articles/views.py


from rest_framework import viewsets, permissions, parsers

from articles.models import Article, ArticleStatus
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer


class ArticlesView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]
    http_method_names = ['get', 'post', ]

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Article.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return Article.objects.none()

        queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)

        return queryset.distinct()
        
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
