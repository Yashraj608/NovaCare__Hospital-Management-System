from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', RedirectView.as_view(url='/accounts/admin-dashboard/', permanent=False)),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('pharmacy/', include('pharmacy.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
