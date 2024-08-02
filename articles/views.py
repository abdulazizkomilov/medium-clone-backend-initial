# articles/views.py
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, parsers, status
from rest_framework.response import Response
from rest_framework import exceptions
from .models import Article, ArticleStatus, TopicFollow, Topic
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer, ArticleListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from articles.filters import ArticleFilter


class ArticlesView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        elif self.action == 'list':
            return ArticleListSerializer
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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user or request.user.is_superuser:
            instance.status = ArticleStatus.TRASH
            instance.save(update_fields=['status'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied()



class TopicFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('id')
        user = request.user

        topic = get_object_or_404(Topic, id=topic_id, is_active=True)

        topic_follow, is_created = TopicFollow.objects.get_or_create(
            user=user, topic=topic)

        if is_created:
            return Response(
                {"detail": _("Siz '{topic_name}' mavzusini kuzatyapsiz.").format(topic_name=topic.name)},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"detail": _("Siz allaqachon '{topic_name}' mavzusini kuzatyapsiz.").format(topic_name=topic.name)},
                status=status.HTTP_200_OK
            )

    def delete(self, request, *args, **kwargs):
        topic_id = self.kwargs.get('id')
        user = request.user

        topic = get_object_or_404(Topic, id=topic_id, is_active=True)

        try:
            topic_follow = TopicFollow.objects.get(user=user, topic=topic)
            topic_follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TopicFollow.DoesNotExist:
            return Response(
                {"detail": _("Siz '{topic_name}' mavzusini kuzatmaysiz.").format(topic_name=topic.name)},
                status=status.HTTP_404_NOT_FOUND
            )