from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from apps.core.mixins import AdminRequiredMixin, ConsultorRequiredMixin, AuditMixin
from .models import EmpresaAncla, UsuarioEmpresaAncla
from .forms import EmpresaAnclaForm, UsuarioEmpresaAnclaForm


class EmpresaAnclaListView(ConsultorRequiredMixin, ListView):
    """Lista de empresas ancla."""
    model = EmpresaAncla
    template_name = 'empresas/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_queryset(self):
        queryset = EmpresaAncla.objects.annotate(
            num_proyectos=Count('proyectos', filter=Q(proyectos__estado='EN_CURSO')),
            num_proveedores=Count('proveedores_vinculados', filter=Q(proveedores_vinculados__estado='ACTIVO'))
        )

        # Si es usuario de empresa ancla, filtrar
        if self.request.user.es_empresa_ancla:
            empresas_ids = self.request.user.empresas_ancla.values_list('empresa_ancla_id', flat=True)
            queryset = queryset.filter(id__in=empresas_ids)

        # Filtros
        sector = self.request.GET.get('sector')
        estado = self.request.GET.get('estado')
        buscar = self.request.GET.get('buscar')

        if sector:
            queryset = queryset.filter(sector_economico=sector)
        if estado:
            queryset = queryset.filter(is_active=(estado == 'activo'))
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(nit__icontains=buscar) |
                Q(ciudad__icontains=buscar)
            )

        return queryset.order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sectores'] = EmpresaAncla.SectorEconomico.choices
        return context


class EmpresaAnclaCreateView(AdminRequiredMixin, AuditMixin, CreateView):
    """Crear nueva empresa ancla."""
    model = EmpresaAncla
    form_class = EmpresaAnclaForm
    template_name = 'empresas/form.html'
    success_url = reverse_lazy('empresas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa ancla creada correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva Empresa Ancla'
        return context


class EmpresaAnclaUpdateView(AdminRequiredMixin, AuditMixin, UpdateView):
    """Editar empresa ancla."""
    model = EmpresaAncla
    form_class = EmpresaAnclaForm
    template_name = 'empresas/form.html'
    success_url = reverse_lazy('empresas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa ancla actualizada correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar: {self.object.nombre}'
        return context


class EmpresaAnclaDetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de empresa ancla."""
    model = EmpresaAncla
    template_name = 'empresas/detalle.html'
    context_object_name = 'empresa'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa = self.object

        # Proyectos de la empresa
        context['proyectos'] = empresa.proyectos.all().order_by('-created_at')[:10]

        # Proveedores vinculados
        context['proveedores'] = empresa.proveedores_vinculados.filter(
            estado='ACTIVO'
        ).select_related('proveedor')[:10]

        # Usuarios asignados
        context['usuarios'] = empresa.usuarios.filter(
            is_active=True
        ).select_related('usuario')

        # Estadísticas
        context['stats'] = {
            'proyectos_activos': empresa.proyectos.filter(estado='EN_CURSO').count(),
            'proyectos_finalizados': empresa.proyectos.filter(estado='FINALIZADO').count(),
            'proveedores_activos': empresa.proveedores_vinculados.filter(estado='ACTIVO').count(),
        }

        return context


class EmpresaAnclaDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar/Desactivar empresa ancla."""
    model = EmpresaAncla
    template_name = 'empresas/confirmar_eliminar.html'
    success_url = reverse_lazy('empresas:lista')

    def form_valid(self, form):
        # En lugar de eliminar, desactivamos
        self.object.is_active = False
        self.object.save()
        messages.success(self.request, 'Empresa ancla desactivada correctamente.')
        return redirect(self.success_url)


# Gestión de usuarios de empresa ancla
class UsuarioEmpresaAnclaCreateView(AdminRequiredMixin, CreateView):
    """Asignar usuario a empresa ancla."""
    model = UsuarioEmpresaAncla
    form_class = UsuarioEmpresaAnclaForm
    template_name = 'empresas/usuario_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa_ancla'] = get_object_or_404(EmpresaAncla, pk=self.kwargs['empresa_pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('empresas:detalle', kwargs={'pk': self.kwargs['empresa_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = get_object_or_404(EmpresaAncla, pk=self.kwargs['empresa_pk'])
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Usuario asignado correctamente.')
        return super().form_valid(form)


def toggle_empresa_activa(request, pk):
    """Activar/Desactivar empresa via AJAX."""
    if not request.user.es_admin:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    empresa = get_object_or_404(EmpresaAncla, pk=pk)
    empresa.is_active = not empresa.is_active
    empresa.save()

    return JsonResponse({
        'success': True,
        'is_active': empresa.is_active,
        'message': f'Empresa {"activada" if empresa.is_active else "desactivada"} correctamente.'
    })
