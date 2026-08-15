"""URL configuration for library_project project."""
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='registration/login.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('', include('library.urls')),
]
