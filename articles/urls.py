# articles/urls.py


from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', views.ArticlesView, basename='articles')


urlpatterns = [
    path('articles/', include(router.urls)),
]
