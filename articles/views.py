# articles/views.py
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, parsers, status, generics
from rest_framework.response import Response
from rest_framework import exceptions
from .models import Article, ArticleStatus, TopicFollow, Topic, Comment, Favorite, Clap, Report, FAQ
from articles.serializers import (
    ArticleCreateSerializer, ArticleDetailSerializer, 
    CommentSerializer, ArticleListSerializer, 
    ArticleDetailCommentsSerializer, ClapSerializer, FAQSerializer )
from django_filters.rest_framework import DjangoFilterBackend
from articles.filters import ArticleFilter
from rest_framework.decorators import action
from users.models import ReadingHistory, Pin


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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        ReadingHistory.objects.get_or_create(
            user=request.user, article=instance      
        )     # ushbu qator qo'shildi

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
		

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def read(self, request, pk=None):
        article = self.get_object()

        article.reads_count += 1
        article.save(update_fields=['reads_count'])
        return Response({"detail": _("Maqolani o'qish soni ortdi.")}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def archive(self, request, pk=None):
        article = self.get_object()
        if article.author == request.user or request.user.is_superuser:
            article.status = ArticleStatus.ARCHIVE
            article.save(update_fields=['status'])
            return Response({"detail": _("Maqola arxivlandi.")}, status=status.HTTP_200_OK)
    
        
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pin(self, request, pk=None):
        article = self.get_object()
        user = request.user
    
        if Pin.objects.filter(user=user, article=article).exists():
            raise exceptions.ValidationError
    
        Pin.objects.create(user=user, article=article)
        return Response({"detail": _("Maqola pin qilindi.")}, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unpin(self, request, pk=None):
        article = self.get_object()
        user = request.user
    
        pin = Pin.objects.filter(user=user, article=article).first()
        if not pin:
            raise exceptions.NotFound(_("Maqola topilmadi.."))
    
        pin.delete()
    
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        

class CreateCommentsView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        article_id = self.kwargs.get('id')
        article = generics.get_object_or_404(Article, id=article_id, status=ArticleStatus.PUBLISH)
        serializer.save(article=article, user=self.request.user)    



# articles/views.py

class CommentsView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch', 'delete']

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user or request.user.is_superuser:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            raise exceptions.PermissionDenied

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == request.user or request.user.is_superuser:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied

    def perform_destroy(self, instance):
        instance.delete()


class ArticleDetailCommentsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleDetailCommentsSerializer

    def get_queryset(self):
        article_id = self.kwargs.get('id')
        return Article.objects.filter(id=article_id)


class FavoriteArticleView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.filter(status=ArticleStatus.PUBLISH)

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        favorite, is_created = Favorite.objects.get_or_create(
            user=request.user, article=article)
        if is_created:
            return Response({'detail': "Maqola sevimlilarga qo'shildi."}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': "Maqola sevimlilarga allaqachon qo'shilgan."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        favorite = get_object_or_404(
            Favorite, user=request.user, article=article)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ClapView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClapSerializer

    def get_queryset(self):
        return Article.objects.filter(status=ArticleStatus.PUBLISH)

    def post(self, request, id):
        user = request.user
        article = get_object_or_404(self.get_queryset(), id=id)

        clap, is_created = Clap.objects.get_or_create(user=user, article=article)
        clap.count = min(clap.count + 1, 50)
        clap.save()

        response_serializer = self.serializer_class(clap)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        article = get_object_or_404(self.get_queryset(), id=id)

        try:
            clap = Clap.objects.get(user=user, article=article)
            clap.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Clap.DoesNotExist:
            raise exceptions.NotFound
        
    
class ReportArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        article_id = kwargs.get('id')

        article = get_object_or_404(Article, id=article_id, status=ArticleStatus.PUBLISH)

        if article.reports.filter(user=user).exists():
            raise exceptions.ValidationError(_('Ushbu maqola allaqachon shikoyat qilingan.'))

        report = Report.objects.create(article=article)
        report.user.add(user)

        unique_reporters_count = article.reports.values('user').distinct().count()

        if unique_reporters_count > 3:
            article.status = ArticleStatus.TRASH
            article.save(update_fields=['status'])
            return Response({"detail": _("Maqola bir nechta shikoyatlar tufayli olib tashlandi.")}, status=status.HTTP_200_OK)

        return Response({"detail": _("Shikoyat yuborildi.")}, status=status.HTTP_201_CREATED)
    
class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]