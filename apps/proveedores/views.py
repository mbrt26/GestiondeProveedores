from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView

from apps.core.mixins import AdminRequiredMixin, ConsultorRequiredMixin, EmpresaAnclaMixin, AuditMixin
from .models import Proveedor, ProveedorEmpresaAncla, DocumentoProveedor
from .forms import ProveedorForm, ProveedorEmpresaAnclaForm, DocumentoProveedorForm, ImportarProveedoresForm


class ProveedorListView(ConsultorRequiredMixin, ListView):
    """Lista de proveedores."""
    model = Proveedor
    template_name = 'proveedores/lista.html'
    context_object_name = 'proveedores'
    paginate_by = 20

    def get_queryset(self):
        queryset = Proveedor.objects.annotate(
            num_proyectos=Count('participaciones', filter=Q(participaciones__estado='EN_PROCESO'))
        )

        # Filtrar por empresa ancla si el usuario es de empresa ancla
        if self.request.user.es_empresa_ancla:
            empresas_ids = self.request.user.empresas_ancla.values_list('empresa_ancla_id', flat=True)
            proveedores_ids = ProveedorEmpresaAncla.objects.filter(
                empresa_ancla_id__in=empresas_ids,
                estado='ACTIVO'
            ).values_list('proveedor_id', flat=True)
            queryset = queryset.filter(id__in=proveedores_ids)

        # Filtros
        sector = self.request.GET.get('sector')
        tamano = self.request.GET.get('tamano')
        ciudad = self.request.GET.get('ciudad')
        empresa_ancla = self.request.GET.get('empresa_ancla')
        buscar = self.request.GET.get('buscar')

        if sector:
            queryset = queryset.filter(sector_economico=sector)
        if tamano:
            queryset = queryset.filter(tamano_empresa=tamano)
        if ciudad:
            queryset = queryset.filter(ciudad__icontains=ciudad)
        if empresa_ancla:
            proveedores_ids = ProveedorEmpresaAncla.objects.filter(
                empresa_ancla_id=empresa_ancla
            ).values_list('proveedor_id', flat=True)
            queryset = queryset.filter(id__in=proveedores_ids)
        if buscar:
            queryset = queryset.filter(
                Q(razon_social__icontains=buscar) |
                Q(nit__icontains=buscar) |
                Q(nombre_comercial__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        return queryset.order_by('razon_social')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sectores'] = Proveedor.SectorEconomico.choices
        context['tamanos'] = Proveedor.TamanoEmpresa.choices

        from apps.empresas.models import EmpresaAncla
        if self.request.user.es_admin or self.request.user.es_consultor:
            context['empresas_ancla'] = EmpresaAncla.objects.filter(is_active=True)
        elif self.request.user.es_empresa_ancla:
            empresas_ids = self.request.user.empresas_ancla.values_list('empresa_ancla_id', flat=True)
            context['empresas_ancla'] = EmpresaAncla.objects.filter(id__in=empresas_ids)

        return context


class ProveedorCreateView(ConsultorRequiredMixin, AuditMixin, CreateView):
    """Crear nuevo proveedor."""
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/form.html'
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo Proveedor'
        return context


class ProveedorUpdateView(ConsultorRequiredMixin, AuditMixin, UpdateView):
    """Editar proveedor."""
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/form.html'
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar: {self.object.nombre_display}'
        return context


class ProveedorDetailView(ConsultorRequiredMixin, DetailView):
    """Detalle de proveedor."""
    model = Proveedor
    template_name = 'proveedores/detalle.html'
    context_object_name = 'proveedor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor = self.object

        # Empresas ancla vinculadas
        context['vinculaciones'] = proveedor.empresas_vinculadas.select_related(
            'empresa_ancla'
        ).order_by('-fecha_vinculacion')

        # Participaciones en proyectos
        context['participaciones'] = proveedor.participaciones.select_related(
            'proyecto', 'consultor_asignado'
        ).order_by('-fecha_inicio')[:10]

        # Documentos
        context['documentos'] = proveedor.documentos.order_by('-uploaded_at')

        # Estadísticas
        context['stats'] = {
            'proyectos_activos': proveedor.participaciones.filter(estado='EN_PROCESO').count(),
            'proyectos_completados': proveedor.participaciones.filter(estado='COMPLETADO').count(),
            'empresas_vinculadas': proveedor.empresas_vinculadas.filter(estado='ACTIVO').count(),
        }

        return context


class ProveedorDeleteView(AdminRequiredMixin, DeleteView):
    """Eliminar proveedor."""
    model = Proveedor
    template_name = 'proveedores/confirmar_eliminar.html'
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor eliminado correctamente.')
        return super().form_valid(form)


# Vinculación con empresas ancla
class VincularEmpresaAnclaView(ConsultorRequiredMixin, CreateView):
    """Vincular proveedor a empresa ancla."""
    model = ProveedorEmpresaAncla
    form_class = ProveedorEmpresaAnclaForm
    template_name = 'proveedores/vincular_empresa.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['proveedor'] = get_object_or_404(Proveedor, pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proveedor'] = get_object_or_404(Proveedor, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor vinculado correctamente.')
        return super().form_valid(form)


# Documentos
class SubirDocumentoView(ConsultorRequiredMixin, CreateView):
    """Subir documento de proveedor."""
    model = DocumentoProveedor
    form_class = DocumentoProveedorForm
    template_name = 'proveedores/subir_documento.html'

    def form_valid(self, form):
        form.instance.proveedor = get_object_or_404(Proveedor, pk=self.kwargs['pk'])
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, 'Documento subido correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proveedor'] = get_object_or_404(Proveedor, pk=self.kwargs['pk'])
        return context


# Importación masiva
class ImportarProveedoresView(AdminRequiredMixin, FormView):
    """Importar proveedores desde Excel."""
    template_name = 'proveedores/importar.html'
    form_class = ImportarProveedoresForm
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        archivo = form.cleaned_data['archivo']
        empresa_ancla = form.cleaned_data.get('empresa_ancla')

        try:
            import pandas as pd

            # Leer archivo Excel
            df = pd.read_excel(archivo)

            creados = 0
            errores = []

            for index, row in df.iterrows():
                try:
                    proveedor, created = Proveedor.objects.update_or_create(
                        nit=str(row.get('nit', '')).strip(),
                        defaults={
                            'razon_social': str(row.get('razon_social', '')).strip(),
                            'nombre_comercial': str(row.get('nombre_comercial', '')).strip(),
                            'representante_legal': str(row.get('representante_legal', '')).strip(),
                            'email': str(row.get('email', '')).strip(),
                            'telefono': str(row.get('telefono', '')).strip(),
                            'direccion': str(row.get('direccion', '')).strip(),
                            'ciudad': str(row.get('ciudad', '')).strip(),
                            'departamento': str(row.get('departamento', '')).strip(),
                            'sector_economico': str(row.get('sector_economico', 'OTRO')).strip().upper(),
                            'numero_empleados': int(row.get('numero_empleados', 1)) if pd.notna(row.get('numero_empleados')) else 1,
                        }
                    )

                    # Vincular a empresa ancla si se especificó
                    if empresa_ancla and created:
                        ProveedorEmpresaAncla.objects.get_or_create(
                            proveedor=proveedor,
                            empresa_ancla=empresa_ancla
                        )

                    if created:
                        creados += 1

                except Exception as e:
                    errores.append(f"Fila {index + 2}: {str(e)}")

            if creados > 0:
                messages.success(self.request, f'Se importaron {creados} proveedores correctamente.')
            if errores:
                messages.warning(self.request, f'Errores encontrados: {len(errores)}. Revise los datos.')

        except Exception as e:
            messages.error(self.request, f'Error al procesar el archivo: {str(e)}')

        return super().form_valid(form)


def descargar_plantilla(request):
    """Descargar plantilla Excel para importación."""
    import pandas as pd
    from io import BytesIO

    # Crear DataFrame con las columnas esperadas
    df = pd.DataFrame(columns=[
        'nit', 'razon_social', 'nombre_comercial', 'representante_legal',
        'email', 'telefono', 'direccion', 'ciudad', 'departamento',
        'sector_economico', 'numero_empleados'
    ])

    # Agregar fila de ejemplo
    df.loc[0] = [
        '900123456-1', 'Empresa Ejemplo SAS', 'Empresa Ejemplo',
        'Juan Pérez', 'contacto@ejemplo.com', '3001234567',
        'Calle 123 #45-67', 'Bogotá', 'Cundinamarca',
        'SERVICIOS', 50
    ]

    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Proveedores')

    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=plantilla_proveedores.xlsx'
    return response
