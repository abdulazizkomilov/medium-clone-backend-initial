# articles/urls.py


from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', views.ArticlesView, basename='articles')
router.register(r'comments', views.CommentsView, basename='comments')


urlpatterns = [
    path('articles/<int:id>/detail/comments/', views.ArticleDetailCommentsView.as_view(), name='article-detail-comments'),
    path('articles/<int:id>/comments/', views.CreateCommentsView.as_view(), name='create_comments'),
    path('articles/topics/<int:id>/follow/', views.TopicFollowView.as_view(), name='topic-follow'),
    path('articles/', include(router.urls)),
]
