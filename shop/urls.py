from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from user_sessions.views import SessionListView, SessionDeleteView

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/sessions/', SessionListView.as_view(), name='session_list'),
    path('accounts/sessions/delete/<pk>/', SessionDeleteView.as_view(), name='session_delete'),
    path('', include('fashion.urls')),  
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

