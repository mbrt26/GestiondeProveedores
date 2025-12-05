"""
URL configuration for gestion_proveedores project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps URLs
    path('', include('apps.core.urls', namespace='core')),
    path('empresas/', include('apps.empresas.urls', namespace='empresas')),
    path('proveedores/', include('apps.proveedores.urls', namespace='proveedores')),
    path('proyectos/', include('apps.proyectos.urls', namespace='proyectos')),
    path('etapas/', include('apps.etapas.urls', namespace='etapas')),
    path('talleres/', include('apps.talleres.urls', namespace='talleres')),
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),
    path('notificaciones/', include('apps.notificaciones.urls', namespace='notificaciones')),

    # API URLs
    path('api/', include('apps.api.urls', namespace='api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
