from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin', admin.site.urls),
    # path('user/', include('fashion.urls'))
    path('', include('fashion.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
