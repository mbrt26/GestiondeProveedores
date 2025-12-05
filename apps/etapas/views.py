from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, CreateView, UpdateView, TemplateView

from apps.core.mixins import ConsultorRequiredMixin
from apps.proyectos.models import ProveedorProyecto
from .models import (
    Etapa1Diagnostico, VozCliente, DiagnosticoCompetitividad, ObjetivoFortalecimiento, DocumentoEtapa1,
    Etapa2Plan, HallazgoProblema, AccionMejora, CronogramaImplementacion,
    Etapa3Implementacion, TareaImplementacion, EvidenciaImplementacion, SesionAcompanamiento,
    Etapa4Monitoreo, IndicadorKPI, MedicionKPI, ReporteSemanal, EvaluacionDirectiva, InformeCierre
)
from .forms import (
    VozClienteForm, DiagnosticoForm, ObjetivoForm, DocumentoEtapa1Form,
    HallazgoForm, AccionMejoraForm, CronogramaForm,
    TareaForm, EvidenciaForm, SesionForm,
    IndicadorForm, MedicionForm, ReporteForm, EvaluacionForm, InformeCierreForm
)


class ProveedorProyectoEtapasView(ConsultorRequiredMixin, DetailView):
    """Vista general del proveedor con todas sus etapas."""
    model = ProveedorProyecto
    template_name = 'etapas/proveedor_etapas.html'
    context_object_name = 'proveedor_proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pp = self.object

        # Obtener o crear etapas
        context['etapa1'], _ = Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=pp)

        try:
            context['etapa2'] = pp.etapa2
        except Etapa2Plan.DoesNotExist:
            context['etapa2'] = None

        try:
            context['etapa3'] = pp.etapa3
        except Etapa3Implementacion.DoesNotExist:
            context['etapa3'] = None

        try:
            context['etapa4'] = pp.etapa4
        except Etapa4Monitoreo.DoesNotExist:
            context['etapa4'] = None

        return context


# ============================================================================
# ETAPA 1: DIAGNÓSTICO
# ============================================================================

class Etapa1DetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de la Etapa 1."""
    model = ProveedorProyecto
    template_name = 'etapas/etapa1/detalle.html'
    context_object_name = 'proveedor_proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etapa1, _ = Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=self.object)
        context['etapa1'] = etapa1
        context['voces_cliente'] = etapa1.voces_cliente.all()
        context['diagnosticos'] = etapa1.diagnosticos.all()
        context['objetivos'] = etapa1.objetivos.all()
        context['documentos'] = etapa1.documentos.all()
        context['areas_evaluadas'] = DiagnosticoCompetitividad.AreaEvaluada.choices
        return context


class VozClienteCreateView(ConsultorRequiredMixin, CreateView):
    """Crear registro de voz del cliente."""
    model = VozCliente
    form_class = VozClienteForm
    template_name = 'etapas/etapa1/voz_cliente_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa1_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa1, _ = Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=pp)
        if etapa1.estado == 'PENDIENTE':
            etapa1.iniciar()
        form.instance.etapa1 = etapa1
        messages.success(self.request, 'Voz del cliente registrada correctamente.')
        return super().form_valid(form)


class DiagnosticoCreateView(ConsultorRequiredMixin, CreateView):
    """Crear diagnóstico de competitividad."""
    model = DiagnosticoCompetitividad
    form_class = DiagnosticoForm
    template_name = 'etapas/etapa1/diagnostico_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa1_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa1, _ = Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=pp)
        form.instance.etapa1 = etapa1
        messages.success(self.request, 'Diagnóstico registrado correctamente.')
        return super().form_valid(form)


class ObjetivoCreateView(ConsultorRequiredMixin, CreateView):
    """Crear objetivo de fortalecimiento."""
    model = ObjetivoFortalecimiento
    form_class = ObjetivoForm
    template_name = 'etapas/etapa1/objetivo_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa1_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa1, _ = Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=pp)
        form.instance.etapa1 = etapa1
        messages.success(self.request, 'Objetivo registrado correctamente.')
        return super().form_valid(form)


class DocumentoEtapa1CreateView(ConsultorRequiredMixin, CreateView):
    """Subir documento de Etapa 1."""
    model = DocumentoEtapa1
    form_class = DocumentoEtapa1Form
    template_name = 'etapas/etapa1/documento_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa1_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa1, _ = Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=pp)
        form.instance.etapa1 = etapa1
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Documento subido correctamente.')
        return super().form_valid(form)


def completar_etapa1(request, pk):
    """Completar Etapa 1 y avanzar a Etapa 2."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    pp = get_object_or_404(ProveedorProyecto, pk=pk)
    etapa1 = get_object_or_404(Etapa1Diagnostico, proveedor_proyecto=pp)

    # Validar que tenga los elementos mínimos
    if not etapa1.voces_cliente.exists():
        return JsonResponse({'error': 'Debe registrar al menos una voz del cliente'}, status=400)
    if not etapa1.diagnosticos.exists():
        return JsonResponse({'error': 'Debe registrar al menos un diagnóstico'}, status=400)
    if not etapa1.objetivos.exists():
        return JsonResponse({'error': 'Debe definir al menos un objetivo'}, status=400)

    etapa1.completar(request.user)
    pp.etapa_actual = 2
    pp.save()

    return JsonResponse({'success': True, 'message': 'Etapa 1 completada. Puede continuar con la Etapa 2.'})


# ============================================================================
# ETAPA 2: PLAN
# ============================================================================

class Etapa2DetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de la Etapa 2."""
    model = ProveedorProyecto
    template_name = 'etapas/etapa2/detalle.html'
    context_object_name = 'proveedor_proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            etapa2 = self.object.etapa2
        except Etapa2Plan.DoesNotExist:
            etapa2 = None
        context['etapa2'] = etapa2
        if etapa2:
            context['hallazgos'] = etapa2.hallazgos.prefetch_related('acciones').all()
            context['cronograma'] = etapa2.cronograma.all()
        return context


class HallazgoCreateView(ConsultorRequiredMixin, CreateView):
    """Crear hallazgo/problema."""
    model = HallazgoProblema
    form_class = HallazgoForm
    template_name = 'etapas/etapa2/hallazgo_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa2_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa2 = get_object_or_404(Etapa2Plan, proveedor_proyecto=pp)
        if etapa2.estado == 'PENDIENTE':
            etapa2.estado = 'EN_PROCESO'
            etapa2.fecha_inicio = timezone.now()
            etapa2.save()
        form.instance.etapa2 = etapa2
        messages.success(self.request, 'Hallazgo registrado correctamente.')
        return super().form_valid(form)


class AccionMejoraCreateView(ConsultorRequiredMixin, CreateView):
    """Crear acción de mejora para un hallazgo."""
    model = AccionMejora
    form_class = AccionMejoraForm
    template_name = 'etapas/etapa2/accion_form.html'

    def get_success_url(self):
        hallazgo = get_object_or_404(HallazgoProblema, pk=self.kwargs['pk'])
        return reverse_lazy('etapas:etapa2_detalle', kwargs={'pk': hallazgo.etapa2.proveedor_proyecto.pk})

    def form_valid(self, form):
        form.instance.hallazgo = get_object_or_404(HallazgoProblema, pk=self.kwargs['pk'])
        messages.success(self.request, 'Acción de mejora registrada correctamente.')
        return super().form_valid(form)


class CronogramaCreateView(ConsultorRequiredMixin, CreateView):
    """Crear item de cronograma."""
    model = CronogramaImplementacion
    form_class = CronogramaForm
    template_name = 'etapas/etapa2/cronograma_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        kwargs['etapa2'] = pp.etapa2
        return kwargs

    def get_success_url(self):
        return reverse_lazy('etapas:etapa2_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        form.instance.etapa2 = pp.etapa2
        messages.success(self.request, 'Actividad agregada al cronograma.')
        return super().form_valid(form)


def aprobar_plan(request, pk):
    """Aprobar el plan de implementación."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    pp = get_object_or_404(ProveedorProyecto, pk=pk)
    etapa2 = get_object_or_404(Etapa2Plan, proveedor_proyecto=pp)

    # Validaciones
    if not etapa2.hallazgos.exists():
        return JsonResponse({'error': 'Debe registrar al menos un hallazgo'}, status=400)
    if not etapa2.cronograma.exists():
        return JsonResponse({'error': 'Debe crear el cronograma de implementación'}, status=400)

    observaciones = request.POST.get('observaciones', '')
    etapa2.aprobar(request.user, observaciones)

    return JsonResponse({'success': True, 'message': 'Plan aprobado. Puede continuar con la Etapa 3.'})


# ============================================================================
# ETAPA 3: IMPLEMENTACIÓN
# ============================================================================

class Etapa3DetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de la Etapa 3 con Kanban."""
    model = ProveedorProyecto
    template_name = 'etapas/etapa3/detalle.html'
    context_object_name = 'proveedor_proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            etapa3 = self.object.etapa3
        except Etapa3Implementacion.DoesNotExist:
            etapa3 = None
        context['etapa3'] = etapa3
        if etapa3:
            context['tareas_pendientes'] = etapa3.tareas.filter(estado='PENDIENTE')
            context['tareas_en_progreso'] = etapa3.tareas.filter(estado='EN_PROGRESO')
            context['tareas_completadas'] = etapa3.tareas.filter(estado='COMPLETADA')
            context['tareas_bloqueadas'] = etapa3.tareas.filter(estado='BLOQUEADA')
            context['sesiones'] = etapa3.sesiones.all()[:5]
        return context


class TareaCreateView(ConsultorRequiredMixin, CreateView):
    """Crear tarea de implementación."""
    model = TareaImplementacion
    form_class = TareaForm
    template_name = 'etapas/etapa3/tarea_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa3_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa3 = get_object_or_404(Etapa3Implementacion, proveedor_proyecto=pp)
        if etapa3.estado == 'PENDIENTE':
            etapa3.estado = 'EN_PROCESO'
            etapa3.fecha_inicio = timezone.now()
            etapa3.save()
        form.instance.etapa3 = etapa3
        messages.success(self.request, 'Tarea creada correctamente.')
        return super().form_valid(form)


class TareaUpdateView(ConsultorRequiredMixin, UpdateView):
    """Editar tarea."""
    model = TareaImplementacion
    form_class = TareaForm
    template_name = 'etapas/etapa3/tarea_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa3_detalle', kwargs={'pk': self.object.etapa3.proveedor_proyecto.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Tarea actualizada correctamente.')
        return super().form_valid(form)


def cambiar_estado_tarea(request, pk):
    """Cambiar estado de tarea (para Kanban)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    tarea = get_object_or_404(TareaImplementacion, pk=pk)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado not in ['PENDIENTE', 'EN_PROGRESO', 'COMPLETADA', 'BLOQUEADA']:
        return JsonResponse({'error': 'Estado no válido'}, status=400)

    tarea.estado = nuevo_estado
    if nuevo_estado == 'COMPLETADA':
        tarea.fecha_fin_real = timezone.now().date()
        tarea.porcentaje_avance = 100
    elif nuevo_estado == 'EN_PROGRESO' and not tarea.fecha_inicio_real:
        tarea.fecha_inicio_real = timezone.now().date()
    tarea.save()

    return JsonResponse({
        'success': True,
        'avance_etapa': float(tarea.etapa3.porcentaje_avance)
    })


class EvidenciaCreateView(ConsultorRequiredMixin, CreateView):
    """Subir evidencia de tarea."""
    model = EvidenciaImplementacion
    form_class = EvidenciaForm
    template_name = 'etapas/etapa3/evidencia_form.html'

    def get_success_url(self):
        tarea = get_object_or_404(TareaImplementacion, pk=self.kwargs['pk'])
        return reverse_lazy('etapas:etapa3_detalle', kwargs={'pk': tarea.etapa3.proveedor_proyecto.pk})

    def form_valid(self, form):
        form.instance.tarea = get_object_or_404(TareaImplementacion, pk=self.kwargs['pk'])
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Evidencia subida correctamente.')
        return super().form_valid(form)


class SesionCreateView(ConsultorRequiredMixin, CreateView):
    """Registrar sesión de acompañamiento."""
    model = SesionAcompanamiento
    form_class = SesionForm
    template_name = 'etapas/etapa3/sesion_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa3_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        form.instance.etapa3 = pp.etapa3
        form.instance.consultor = self.request.user
        messages.success(self.request, 'Sesión registrada correctamente.')
        return super().form_valid(form)


def kanban_data(request, pk):
    """Datos para actualizar el tablero Kanban."""
    pp = get_object_or_404(ProveedorProyecto, pk=pk)
    etapa3 = pp.etapa3

    data = {
        'avance': float(etapa3.porcentaje_avance),
        'tareas': {
            'pendientes': list(etapa3.tareas.filter(estado='PENDIENTE').values('id', 'titulo', 'prioridad')),
            'en_progreso': list(etapa3.tareas.filter(estado='EN_PROGRESO').values('id', 'titulo', 'prioridad')),
            'completadas': list(etapa3.tareas.filter(estado='COMPLETADA').values('id', 'titulo', 'prioridad')),
            'bloqueadas': list(etapa3.tareas.filter(estado='BLOQUEADA').values('id', 'titulo', 'prioridad')),
        }
    }
    return JsonResponse(data)


# ============================================================================
# ETAPA 4: MONITOREO
# ============================================================================

class Etapa4DetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de la Etapa 4 con KPIs."""
    model = ProveedorProyecto
    template_name = 'etapas/etapa4/detalle.html'
    context_object_name = 'proveedor_proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            etapa4 = self.object.etapa4
        except Etapa4Monitoreo.DoesNotExist:
            etapa4 = None
        context['etapa4'] = etapa4
        if etapa4:
            context['indicadores'] = etapa4.indicadores.all()
            context['reportes'] = etapa4.reportes_semanales.all()[:5]
            context['evaluaciones'] = etapa4.evaluaciones.all()[:3]
            try:
                context['informe_cierre'] = etapa4.informe_cierre
            except InformeCierre.DoesNotExist:
                context['informe_cierre'] = None
        return context


class IndicadorCreateView(ConsultorRequiredMixin, CreateView):
    """Crear indicador KPI."""
    model = IndicadorKPI
    form_class = IndicadorForm
    template_name = 'etapas/etapa4/indicador_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        kwargs['etapa1'] = pp.etapa1
        return kwargs

    def get_success_url(self):
        return reverse_lazy('etapas:etapa4_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        etapa4 = get_object_or_404(Etapa4Monitoreo, proveedor_proyecto=pp)
        if etapa4.estado == 'PENDIENTE':
            etapa4.estado = 'EN_PROCESO'
            etapa4.fecha_inicio = timezone.now()
            etapa4.save()
        form.instance.etapa4 = etapa4
        messages.success(self.request, 'Indicador creado correctamente.')
        return super().form_valid(form)


class MedicionCreateView(ConsultorRequiredMixin, CreateView):
    """Registrar medición de KPI."""
    model = MedicionKPI
    form_class = MedicionForm
    template_name = 'etapas/etapa4/medicion_form.html'

    def get_success_url(self):
        indicador = get_object_or_404(IndicadorKPI, pk=self.kwargs['pk'])
        return reverse_lazy('etapas:etapa4_detalle', kwargs={'pk': indicador.etapa4.proveedor_proyecto.pk})

    def form_valid(self, form):
        form.instance.indicador = get_object_or_404(IndicadorKPI, pk=self.kwargs['pk'])
        form.instance.registrado_por = self.request.user
        messages.success(self.request, 'Medición registrada correctamente.')
        return super().form_valid(form)


class ReporteCreateView(ConsultorRequiredMixin, CreateView):
    """Crear reporte semanal."""
    model = ReporteSemanal
    form_class = ReporteForm
    template_name = 'etapas/etapa4/reporte_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa4_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        form.instance.etapa4 = pp.etapa4
        messages.success(self.request, 'Reporte creado correctamente.')
        return super().form_valid(form)


class EvaluacionCreateView(ConsultorRequiredMixin, CreateView):
    """Crear evaluación directiva."""
    model = EvaluacionDirectiva
    form_class = EvaluacionForm
    template_name = 'etapas/etapa4/evaluacion_form.html'

    def get_success_url(self):
        return reverse_lazy('etapas:etapa4_detalle', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        pp = get_object_or_404(ProveedorProyecto, pk=self.kwargs['pk'])
        form.instance.etapa4 = pp.etapa4
        messages.success(self.request, 'Evaluación registrada correctamente.')
        return super().form_valid(form)


def generar_informe_cierre(request, pk):
    """Generar informe de cierre."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    pp = get_object_or_404(ProveedorProyecto, pk=pk)
    etapa4 = get_object_or_404(Etapa4Monitoreo, proveedor_proyecto=pp)

    # Recopilar datos para el informe
    kpis_data = {}
    for ind in etapa4.indicadores.all():
        kpis_data[ind.nombre] = {
            'inicial': float(ind.valor_inicial),
            'final': float(ind.valor_actual),
            'meta': float(ind.valor_meta),
            'cumplimiento': ind.porcentaje_cumplimiento
        }

    informe, created = InformeCierre.objects.get_or_create(
        etapa4=etapa4,
        defaults={
            'resumen_ejecutivo': request.POST.get('resumen', ''),
            'objetivos_logrados': request.POST.get('objetivos_logrados', ''),
            'mejoras_implementadas': request.POST.get('mejoras', ''),
            'resultados_kpis': kpis_data,
            'lecciones_aprendidas': request.POST.get('lecciones', ''),
            'recomendaciones': request.POST.get('recomendaciones', ''),
        }
    )

    etapa4.informe_final_generado = True
    etapa4.save()

    return JsonResponse({'success': True, 'informe_id': str(informe.id)})


def completar_etapa4(request, pk):
    """Completar Etapa 4 y cerrar el fortalecimiento."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    pp = get_object_or_404(ProveedorProyecto, pk=pk)
    etapa4 = get_object_or_404(Etapa4Monitoreo, proveedor_proyecto=pp)

    if not etapa4.informe_final_generado:
        return JsonResponse({'error': 'Debe generar el informe de cierre primero'}, status=400)

    etapa4.completar()

    return JsonResponse({'success': True, 'message': 'Fortalecimiento completado exitosamente.'})


def kpis_chart_data(request, pk):
    """Datos para gráficos de KPIs."""
    pp = get_object_or_404(ProveedorProyecto, pk=pk)
    etapa4 = pp.etapa4

    indicadores = []
    for ind in etapa4.indicadores.all():
        mediciones = list(ind.mediciones.order_by('fecha_medicion').values('fecha_medicion', 'valor'))
        indicadores.append({
            'nombre': ind.nombre,
            'valor_inicial': float(ind.valor_inicial),
            'valor_actual': float(ind.valor_actual),
            'valor_meta': float(ind.valor_meta),
            'cumplimiento': ind.porcentaje_cumplimiento,
            'tendencia': ind.tendencia,
            'mediciones': [{'fecha': m['fecha_medicion'].isoformat(), 'valor': float(m['valor'])} for m in mediciones]
        })

    return JsonResponse({'indicadores': indicadores})
