from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Usuario, LogActividad


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registrar inicio de sesión."""
    LogActividad.objects.create(
        usuario=user,
        accion=LogActividad.Accion.LOGIN,
        descripcion=f'Inicio de sesión: {user.email}',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Registrar cierre de sesión."""
    if user:
        LogActividad.objects.create(
            usuario=user,
            accion=LogActividad.Accion.LOGOUT,
            descripcion=f'Cierre de sesión: {user.email}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )


def get_client_ip(request):
    """Obtener IP del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
