"""
URL configuration for jln_hub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Define template views for each page
def template_view(template_name):
    return TemplateView.as_view(template_name=template_name)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    # Main pages
    path('', template_view('index.html'), name='index'),
    path('home.html', template_view('home.html'), name='home'),
    path('subjects.html', template_view('subjects.html'), name='subjects'),
    path('lessons.html', template_view('lessons.html'), name='lessons'),
    path('lesson-detail.html', template_view('lesson-detail.html'), name='lesson-detail'),
    path('quizzes.html', template_view('quizzes.html'), name='quizzes'),
    path('simulations.html', template_view('simulations.html'), name='simulations'),
    path('progress.html', template_view('progress.html'), name='progress'),
    path('admin-dashboard.html', template_view('admin-dashboard.html'), name='admin-dashboard'),
    path('lesson-generator.html', template_view('lesson-generator.html'), name='lesson-generator'),
    
    # Auth pages (in src/pages/)
    path('src/pages/login.html', template_view('src/pages/login.html'), name='login'),
    path('src/pages/register.html', template_view('src/pages/register.html'), name='register'),
]

# Serve media files in development
# Note: Static files are automatically served by Django's staticfiles app when DEBUG=True
# from STATICFILES_DIRS (no need to manually add static file serving)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
