from django.conf import settings


def global_settings(request):
    """Context processor para variables globales."""
    return {
        'APP_NAME': getattr(settings, 'APP_NAME', 'Sistema de Fortalecimiento de Proveedores'),
        'APP_SHORT_NAME': getattr(settings, 'APP_SHORT_NAME', 'SFP'),
        'APP_VERSION': getattr(settings, 'APP_VERSION', '1.0.0'),
        'ETAPAS': getattr(settings, 'ETAPAS', {}),
    }
