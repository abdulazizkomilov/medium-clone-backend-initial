# articles/filters.py

import django_filters
from .models import Article


class ArticleFilter(django_filters.FilterSet):
    get_top_articles = django_filters.NumberFilter(method='filter_by_top')
    topic_id = django_filters.NumberFilter(method='filter_by_topic')

    class Meta:
        model = Article
        fields = ['get_top_articles', 'topic_id']

    def filter_by_top(self, queryset, name, value):
        return queryset.order_by('-views_count')[:value]

    def filter_by_topic(self, queryset, name, value):
        return queryset.filter(topics__id=value)
