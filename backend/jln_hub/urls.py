"""
URL configuration for jln_hub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

# Serve media files in development
# Note: Static files are automatically served by Django's staticfiles app when DEBUG=True
# from STATICFILES_DIRS (no need to manually add static file serving)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
