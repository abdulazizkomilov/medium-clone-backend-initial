# articles/serializers.py

from rest_framework import serializers

from articles.models import Topic, Clap, Article, ArticleStatus
from users.serializers import UserSerializer


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']


class ClapSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Clap
        fields = ['user', 'article', 'count']


class ArticleCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.filter(is_active=True), many=True, write_only=True, required=True
    )
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content',
                  'status', 'thumbnail', 'topic_ids', 'topics', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        article = Article.objects.create(**validated_data, status=ArticleStatus.PENDING)
        article.topics.set(topic_ids)
        return article


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    topics = TopicSerializer(many=True)
    claps = ClapSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count', 'reads_count',
                  'created_at', 'updated_at', 'topics', 'claps']
