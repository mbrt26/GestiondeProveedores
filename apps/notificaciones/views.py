from django.http import JsonResponse
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import Notificacion, ConfiguracionNotificacion


class NotificacionListView(LoginRequiredMixin, ListView):
    """Lista de notificaciones del usuario."""
    model = Notificacion
    template_name = 'notificaciones/lista.html'
    context_object_name = 'notificaciones'
    paginate_by = 20

    def get_queryset(self):
        return Notificacion.objects.filter(
            usuario=self.request.user,
            tipo=Notificacion.tipo.field.choices[2][0]  # SISTEMA
        ).select_related('plantilla')


class NotificacionesNoLeidasView(LoginRequiredMixin, View):
    """API para obtener notificaciones no leídas."""

    def get(self, request):
        notificaciones = Notificacion.objects.filter(
            usuario=request.user,
            estado__in=['PENDIENTE', 'ENVIADA']
        ).values('id', 'titulo', 'mensaje', 'enlace', 'created_at')[:10]

        return JsonResponse({
            'count': notificaciones.count(),
            'notificaciones': list(notificaciones)
        })


class MarcarLeidaView(LoginRequiredMixin, View):
    """Marcar notificación como leída."""

    def post(self, request, pk):
        try:
            notificacion = Notificacion.objects.get(pk=pk, usuario=request.user)
            notificacion.marcar_como_leida()
            return JsonResponse({'success': True})
        except Notificacion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notificación no encontrada'}, status=404)


class MarcarTodasLeidasView(LoginRequiredMixin, View):
    """Marcar todas las notificaciones como leídas."""

    def post(self, request):
        Notificacion.objects.filter(
            usuario=request.user,
            estado__in=['PENDIENTE', 'ENVIADA']
        ).update(estado='LEIDA', fecha_lectura=timezone.now())

        return JsonResponse({'success': True})


class ConfiguracionNotificacionView(LoginRequiredMixin, View):
    """Configuración de notificaciones del usuario."""

    def get(self, request):
        config, created = ConfiguracionNotificacion.objects.get_or_create(
            usuario=request.user
        )
        return JsonResponse({
            'email_activo': config.email_activo,
            'whatsapp_activo': config.whatsapp_activo,
            'sistema_activo': config.sistema_activo,
            'notificar_tareas': config.notificar_tareas,
            'notificar_sesiones': config.notificar_sesiones,
            'notificar_talleres': config.notificar_talleres,
            'notificar_reportes': config.notificar_reportes,
            'notificar_alertas': config.notificar_alertas,
        })

    def post(self, request):
        config, created = ConfiguracionNotificacion.objects.get_or_create(
            usuario=request.user
        )

        # Actualizar configuración desde el request
        for field in ['email_activo', 'whatsapp_activo', 'sistema_activo',
                      'notificar_tareas', 'notificar_sesiones', 'notificar_talleres',
                      'notificar_reportes', 'notificar_alertas']:
            if field in request.POST:
                setattr(config, field, request.POST.get(field) == 'true')

        config.save()
        return JsonResponse({'success': True})
