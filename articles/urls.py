# articles/urls.py


from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', views.ArticlesView, basename='articles')


urlpatterns = [
    path('articles/topics/<int:id>/follow/', views.TopicFollowView.as_view(), name='topic-follow'),
    path('articles/', include(router.urls)),
]
