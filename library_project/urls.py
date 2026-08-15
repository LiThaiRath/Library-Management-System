"""URL configuration for library_project project."""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='home'),
    path('accounts/', include('accounts.urls')),
    path('', include('library.urls')),
]
