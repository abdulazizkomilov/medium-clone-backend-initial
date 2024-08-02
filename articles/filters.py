# articles/filters.py
from django.db import models
import django_filters
from .models import Article, Favorite, Pin
from users.models import Recommendation, ReadingHistory
from django.db.models import Q


class ArticleFilter(django_filters.FilterSet):
    get_top_articles = django_filters.NumberFilter(method='filter_by_top')
    topic_id = django_filters.NumberFilter(method='filter_by_topic')
    is_recommend = django_filters.BooleanFilter(method='filter_by_recommend')
    search = django_filters.CharFilter(method='search_filter')
    is_user_favorites = django_filters.BooleanFilter(method='user_favorites')
    is_reading_history = django_filters.BooleanFilter(method='user_reading_history')
    is_author_articles = django_filters.BooleanFilter(method='author_articles')

    class Meta:
        model = Article
        fields = ['get_top_articles', 'topic_id', 'is_recommend']

    def filter_by_top(self, queryset, name, value):
        return queryset.order_by('-views_count')[:value]

    def filter_by_recommend(self, queryset, name, value):
        user = self.request.user
        recommendations = Recommendation.objects.filter(user=user)
        more_topics = recommendations.values_list('more', flat=True)
        less_topics = recommendations.values_list('less', flat=True)


        if more_topics.exists():
            queryset = queryset.filter(Q(topics__in=more_topics))

        if less_topics.exists():
            queryset = queryset.exclude(topics__in=less_topics)

        return queryset

    def filter_by_topic(self, queryset, name, value):
        return queryset.filter(topics__id=value)
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(summary__icontains=value) |
            Q(content__icontains=value) |
            Q(topics__name__icontains=value) |
            Q(topics__description__icontains=value)
        ).distinct()
    
    def user_favorites(self, queryset, name, value):
        favorites = Favorite.objects.filter(user=self.request.user).order_by('-created_at')
        article_ids = favorites.values_list('article_id', flat=True)
        return queryset.filter(id__in=article_ids)
    
    def user_reading_history(self, queryset, name, value):
        reading_history = ReadingHistory.objects.filter(user=self.request.user).order_by('-created_at')
        article_ids = reading_history.values_list('article_id', flat=True)
        return queryset.filter(id__in=article_ids)

    def author_articles(self, queryset, name, value):
        user = self.request.user

        queryset = Article.objects.filter(author=user)
        pin_subquery = Pin.objects.filter(article=models.OuterRef('pk'), user=user)
        queryset = queryset.annotate(
            is_pinned=models.Exists(pin_subquery)
        )
        queryset = queryset.order_by('-is_pinned', '-created_at')
        return queryset