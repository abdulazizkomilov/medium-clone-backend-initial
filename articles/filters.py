# articles/filters.py

import django_filters
from .models import Article
from users.models import Recommendation
from django.db.models import Q


class ArticleFilter(django_filters.FilterSet):
    get_top_articles = django_filters.NumberFilter(method='filter_by_top')
    topic_id = django_filters.NumberFilter(method='filter_by_topic')
    is_recommend = django_filters.BooleanFilter(method='filter_by_recommend')
    search = django_filters.CharFilter(method='search_filter')

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
