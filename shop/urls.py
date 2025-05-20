from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from user_sessions.views import SessionListView, SessionDeleteView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  
]

urlpatterns += i18n_patterns(
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('accounts/sessions/', SessionListView.as_view(), name='session_list'),
    path('accounts/sessions/delete/<pk>/', SessionDeleteView.as_view(), name='session_delete'),
    path('', include('fashion.urls')),  
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
