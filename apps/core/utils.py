import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_unique_code(prefix='', length=8):
    """Generar código único."""
    unique_id = uuid.uuid4().hex[:length].upper()
    return f"{prefix}{unique_id}" if prefix else unique_id


def send_email_notification(
    subject,
    template_name,
    context,
    recipient_list,
    from_email=None
):
    """
    Enviar notificación por email usando plantilla HTML.

    Args:
        subject: Asunto del email
        template_name: Nombre de la plantilla (sin extensión)
        context: Contexto para la plantilla
        recipient_list: Lista de destinatarios
        from_email: Email del remitente (opcional)
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    html_message = render_to_string(f'emails/{template_name}.html', context)
    plain_message = strip_tags(html_message)

    return send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False
    )


def get_client_ip(request):
    """Obtener IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def format_currency(value, currency='COP'):
    """Formatear valor como moneda colombiana."""
    try:
        value = float(value)
        if currency == 'COP':
            return f"${value:,.0f}".replace(',', '.')
        return f"{currency} {value:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value, decimals=1):
    """Formatear valor como porcentaje."""
    try:
        value = float(value)
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def truncate_string(text, max_length=50, suffix='...'):
    """Truncar texto a una longitud máxima."""
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


class LogActivityMixin:
    """Mixin para registrar actividad en vistas."""

    def log_activity(self, accion, descripcion, modelo='', objeto_id='', datos_anteriores=None, datos_nuevos=None):
        from .models import LogActividad

        LogActividad.objects.create(
            usuario=self.request.user if self.request.user.is_authenticated else None,
            accion=accion,
            modelo=modelo,
            objeto_id=str(objeto_id),
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
