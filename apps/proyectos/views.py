from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, View

from apps.core.mixins import AdminRequiredMixin, ConsultorRequiredMixin, EmpresaAnclaMixin, AuditMixin
from .models import Proyecto, ProveedorProyecto, DocumentoProyecto
from .forms import (
    ProyectoForm, ProveedorProyectoForm, AsignarMultiplesProveedoresForm,
    CambiarConsultorForm, DocumentoProyectoForm
)


class ProyectoListView(ConsultorRequiredMixin, EmpresaAnclaMixin, ListView):
    """Lista de proyectos."""
    model = Proyecto
    template_name = 'proyectos/lista.html'
    context_object_name = 'proyectos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            num_proveedores=Count('proveedores'),
            avance_promedio=Avg('proveedores__porcentaje_avance')
        )

        # Filtros
        estado = self.request.GET.get('estado')
        empresa = self.request.GET.get('empresa')
        buscar = self.request.GET.get('buscar')

        if estado:
            queryset = queryset.filter(estado=estado)
        if empresa:
            queryset = queryset.filter(empresa_ancla_id=empresa)
        if buscar:
            queryset = queryset.filter(
                Q(codigo__icontains=buscar) |
                Q(nombre__icontains=buscar) |
                Q(empresa_ancla__nombre__icontains=buscar)
            )

        return queryset.order_by('-fecha_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Proyecto.EstadoProyecto.choices

        from apps.empresas.models import EmpresaAncla
        if self.request.user.es_admin or self.request.user.es_consultor:
            context['empresas'] = EmpresaAncla.objects.filter(is_active=True)
        elif self.request.user.es_empresa_ancla:
            empresas_ids = self.request.user.empresas_ancla.values_list('empresa_ancla_id', flat=True)
            context['empresas'] = EmpresaAncla.objects.filter(id__in=empresas_ids)

        return context


class ProyectoCreateView(ConsultorRequiredMixin, AuditMixin, CreateView):
    """Crear nuevo proyecto."""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/form.html'
    success_url = reverse_lazy('proyectos:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto creado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo Proyecto'
        return context


class ProyectoUpdateView(ConsultorRequiredMixin, AuditMixin, UpdateView):
    """Editar proyecto."""
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'proyectos/form.html'

    def get_success_url(self):
        return reverse_lazy('proyectos:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto actualizado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar: {self.object.nombre}'
        return context


class ProyectoDetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de proyecto."""
    model = Proyecto
    template_name = 'proyectos/detalle.html'
    context_object_name = 'proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = self.object

        # Proveedores del proyecto
        context['proveedores_proyecto'] = proyecto.proveedores.select_related(
            'proveedor', 'consultor_asignado'
        ).order_by('proveedor__razon_social')

        # Documentos
        context['documentos'] = proyecto.documentos.order_by('-uploaded_at')

        # Estadísticas
        context['stats'] = {
            'total_proveedores': proyecto.proveedores.count(),
            'en_proceso': proyecto.proveedores.filter(estado='EN_PROCESO').count(),
            'completados': proyecto.proveedores.filter(estado='COMPLETADO').count(),
            'etapa_1': proyecto.proveedores.filter(etapa_actual=1).count(),
            'etapa_2': proyecto.proveedores.filter(etapa_actual=2).count(),
            'etapa_3': proyecto.proveedores.filter(etapa_actual=3).count(),
            'etapa_4': proyecto.proveedores.filter(etapa_actual=4).count(),
            'avance_promedio': proyecto.avance_promedio,
        }

        return context


class ProyectoDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar/Cancelar proyecto."""
    model = Proyecto
    template_name = 'proyectos/confirmar_eliminar.html'
    success_url = reverse_lazy('proyectos:lista')

    def form_valid(self, form):
        # En lugar de eliminar, cancelamos
        self.object.estado = 'CANCELADO'
        self.object.save()
        messages.success(self.request, 'Proyecto cancelado correctamente.')
        return redirect(self.success_url)


# Gestión de proveedores en proyecto
class AsignarProveedorView(ConsultorRequiredMixin, CreateView):
    """Asignar un proveedor al proyecto."""
    model = ProveedorProyecto
    form_class = ProveedorProyectoForm
    template_name = 'proyectos/asignar_proveedor.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['proyecto'] = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('proyectos:detalle', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyecto'] = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor asignado correctamente.')
        return super().form_valid(form)


class AsignarMultiplesProveedoresView(ConsultorRequiredMixin, FormView):
    """Asignar múltiples proveedores al proyecto."""
    template_name = 'proyectos/asignar_multiples.html'
    form_class = AsignarMultiplesProveedoresForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['proyecto'] = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('proyectos:detalle', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyecto'] = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        proveedores = form.cleaned_data['proveedores']
        consultor = form.cleaned_data.get('consultor_asignado')
        fecha_inicio = form.cleaned_data.get('fecha_inicio')

        for proveedor in proveedores:
            ProveedorProyecto.objects.create(
                proyecto=proyecto,
                proveedor=proveedor,
                consultor_asignado=consultor,
                fecha_inicio=fecha_inicio,
                horas_planeadas=proyecto.horas_por_proveedor
            )

        messages.success(self.request, f'{len(proveedores)} proveedores asignados correctamente.')
        return super().form_valid(form)


class RemoverProveedorView(ConsultorRequiredMixin, View):
    """Remover proveedor del proyecto."""

    def post(self, request, pk, proveedor_pk):
        proveedor_proyecto = get_object_or_404(
            ProveedorProyecto,
            proyecto_id=pk,
            pk=proveedor_pk
        )

        if proveedor_proyecto.estado in ['COMPLETADO', 'EN_PROCESO']:
            proveedor_proyecto.estado = 'RETIRADO'
            proveedor_proyecto.save()
            messages.warning(request, 'Proveedor marcado como retirado.')
        else:
            proveedor_proyecto.delete()
            messages.success(request, 'Proveedor removido del proyecto.')

        return redirect('proyectos:detalle', pk=pk)


class CambiarConsultorView(ConsultorRequiredMixin, FormView):
    """Cambiar consultor de un proveedor en proyecto."""
    template_name = 'proyectos/cambiar_consultor.html'
    form_class = CambiarConsultorForm

    def get_success_url(self):
        return reverse_lazy('proyectos:detalle', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyecto'] = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        context['proveedor_proyecto'] = get_object_or_404(
            ProveedorProyecto,
            pk=self.kwargs['proveedor_pk']
        )
        return context

    def form_valid(self, form):
        proveedor_proyecto = get_object_or_404(
            ProveedorProyecto,
            pk=self.kwargs['proveedor_pk']
        )
        proveedor_proyecto.consultor_asignado = form.cleaned_data['consultor_asignado']
        proveedor_proyecto.save()
        messages.success(self.request, 'Consultor cambiado correctamente.')
        return super().form_valid(form)


# Documentos del proyecto
class SubirDocumentoProyectoView(ConsultorRequiredMixin, CreateView):
    """Subir documento al proyecto."""
    model = DocumentoProyecto
    form_class = DocumentoProyectoForm
    template_name = 'proyectos/subir_documento.html'

    def get_success_url(self):
        return reverse_lazy('proyectos:detalle', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proyecto'] = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk'])
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Documento subido correctamente.')
        return super().form_valid(form)


# API endpoints
def proyecto_dashboard_data(request, pk):
    """Datos para el dashboard del proyecto (AJAX)."""
    proyecto = get_object_or_404(Proyecto, pk=pk)

    data = {
        'avance_promedio': float(proyecto.avance_promedio or 0),
        'proveedores_por_etapa': {
            'etapa_1': proyecto.proveedores.filter(etapa_actual=1).count(),
            'etapa_2': proyecto.proveedores.filter(etapa_actual=2).count(),
            'etapa_3': proyecto.proveedores.filter(etapa_actual=3).count(),
            'etapa_4': proyecto.proveedores.filter(etapa_actual=4).count(),
        },
        'proveedores_por_estado': {
            'pendiente': proyecto.proveedores.filter(estado='PENDIENTE').count(),
            'en_proceso': proyecto.proveedores.filter(estado='EN_PROCESO').count(),
            'completado': proyecto.proveedores.filter(estado='COMPLETADO').count(),
            'suspendido': proyecto.proveedores.filter(estado='SUSPENDIDO').count(),
        },
        'dias_restantes': proyecto.dias_restantes,
    }

    return JsonResponse(data)


def iniciar_proveedor(request, pk, proveedor_pk):
    """Iniciar el proceso de fortalecimiento de un proveedor."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    proveedor_proyecto = get_object_or_404(ProveedorProyecto, pk=proveedor_pk, proyecto_id=pk)

    if proveedor_proyecto.estado != 'PENDIENTE':
        return JsonResponse({'error': 'El proveedor ya fue iniciado'}, status=400)

    proveedor_proyecto.estado = 'EN_PROCESO'
    if not proveedor_proyecto.fecha_inicio:
        from django.utils import timezone
        proveedor_proyecto.fecha_inicio = timezone.now().date()
    proveedor_proyecto.save()

    # Crear registro de Etapa 1 si no existe
    from apps.etapas.models import Etapa1Diagnostico
    Etapa1Diagnostico.objects.get_or_create(proveedor_proyecto=proveedor_proyecto)

    return JsonResponse({'success': True, 'message': 'Proceso iniciado correctamente'})
