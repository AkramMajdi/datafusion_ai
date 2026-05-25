from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('etl/upload/')),
    path('core/login/', auth_views.LoginView.as_view(
        template_name='core/login.html'
    ), name='login'),
    path('core/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('core/', include('core.urls')),
    path('etl/', include('etl.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)