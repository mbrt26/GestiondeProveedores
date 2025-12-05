from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from apps.core.mixins import ConsultorRequiredMixin
from .models import Taller, SesionTaller, InscripcionTaller, AsistenciaTaller, CertificadoTaller, EvaluacionTaller


class TallerListView(ConsultorRequiredMixin, ListView):
    model = Taller
    template_name = 'talleres/lista.html'
    context_object_name = 'talleres'
    paginate_by = 20

    def get_queryset(self):
        return Taller.objects.filter(is_active=True).order_by('-created_at')


class TallerCreateView(ConsultorRequiredMixin, CreateView):
    model = Taller
    template_name = 'talleres/form.html'
    fields = ['nombre', 'tipo', 'descripcion', 'contenido_programatico', 'objetivos',
              'duracion_horas', 'modalidad', 'capacidad_maxima', 'facilitador', 'proyecto', 'material_didactico']
    success_url = reverse_lazy('talleres:lista')


class TallerUpdateView(ConsultorRequiredMixin, UpdateView):
    model = Taller
    template_name = 'talleres/form.html'
    fields = ['nombre', 'tipo', 'descripcion', 'contenido_programatico', 'objetivos',
              'duracion_horas', 'modalidad', 'capacidad_maxima', 'facilitador', 'material_didactico', 'is_active']

    def get_success_url(self):
        return reverse_lazy('talleres:detalle', kwargs={'pk': self.object.pk})


class TallerDetailView(ConsultorRequiredMixin, DetailView):
    model = Taller
    template_name = 'talleres/detalle.html'
    context_object_name = 'taller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sesiones'] = self.object.sesiones.order_by('-fecha')
        return context


class SesionCreateView(ConsultorRequiredMixin, CreateView):
    model = SesionTaller
    template_name = 'talleres/sesion_form.html'
    fields = ['fecha', 'hora_inicio', 'hora_fin', 'lugar', 'notas']

    def form_valid(self, form):
        form.instance.taller = get_object_or_404(Taller, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('talleres:detalle', kwargs={'pk': self.kwargs['pk']})


class InscripcionCreateView(ConsultorRequiredMixin, CreateView):
    model = InscripcionTaller
    template_name = 'talleres/inscripcion_form.html'
    fields = ['proveedor', 'participante_nombre', 'participante_email', 'participante_cargo']

    def form_valid(self, form):
        form.instance.sesion = get_object_or_404(SesionTaller, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        sesion = get_object_or_404(SesionTaller, pk=self.kwargs['pk'])
        return reverse_lazy('talleres:detalle', kwargs={'pk': sesion.taller.pk})


def registrar_asistencia(request, pk):
    """Registrar asistencia de una sesión."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    sesion = get_object_or_404(SesionTaller, pk=pk)
    inscripcion_ids = request.POST.getlist('inscripciones')

    for inscripcion in sesion.inscripciones.all():
        asistio = str(inscripcion.id) in inscripcion_ids
        AsistenciaTaller.objects.update_or_create(
            inscripcion=inscripcion,
            defaults={'asistio': asistio}
        )
        inscripcion.estado = 'ASISTIO' if asistio else 'NO_ASISTIO'
        inscripcion.save()

    sesion.estado = 'FINALIZADA'
    sesion.save()

    return JsonResponse({'success': True})


def generar_certificado(request, pk):
    """Generar certificado para un participante."""
    inscripcion = get_object_or_404(InscripcionTaller, pk=pk)

    if not hasattr(inscripcion, 'asistencia') or not inscripcion.asistencia.asistio:
        return JsonResponse({'error': 'El participante no asistió al taller'}, status=400)

    import uuid
    certificado, created = CertificadoTaller.objects.get_or_create(
        inscripcion=inscripcion,
        defaults={'codigo_certificado': f"CERT-{uuid.uuid4().hex[:8].upper()}"}
    )

    return JsonResponse({'success': True, 'codigo': certificado.codigo_certificado})


class EvaluacionCreateView(ConsultorRequiredMixin, CreateView):
    model = EvaluacionTaller
    template_name = 'talleres/evaluacion_form.html'
    fields = ['calificacion_general', 'calificacion_facilitador', 'calificacion_contenido',
              'calificacion_logistica', 'comentarios', 'sugerencias']

    def form_valid(self, form):
        form.instance.inscripcion = get_object_or_404(InscripcionTaller, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('talleres:lista')
