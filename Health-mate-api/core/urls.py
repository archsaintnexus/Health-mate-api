from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def api_root(request):
    return JsonResponse({
        "message": "Welcome to Health Mate API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs/",
        "endpoints": {
            "auth": "/auth/",
            "admin": "/admin/",
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls', namespace='accounts')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
