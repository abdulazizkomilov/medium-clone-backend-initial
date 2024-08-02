from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.http import JsonResponse

urlpatterns = [
    path("admin/", admin.site.urls),
    path('health/', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)