from django.contrib import admin
from .models import Proyecto, ProveedorProyecto, DocumentoProyecto


class ProveedorProyectoInline(admin.TabularInline):
    """Inline para proveedores del proyecto."""
    model = ProveedorProyecto
    extra = 0
    autocomplete_fields = ['proveedor', 'consultor_asignado']
    readonly_fields = ['porcentaje_avance', 'horas_consumidas']


class DocumentoProyectoInline(admin.TabularInline):
    """Inline para documentos del proyecto."""
    model = DocumentoProyecto
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by']


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """Admin para Proyecto."""

    list_display = (
        'codigo', 'nombre', 'empresa_ancla', 'estado',
        'fecha_inicio', 'fecha_fin_planeada', 'proveedores_count'
    )
    list_filter = ('estado', 'empresa_ancla', 'fecha_inicio')
    search_fields = ('codigo', 'nombre', 'empresa_ancla__nombre')
    ordering = ('-fecha_inicio',)
    readonly_fields = ['codigo']
    autocomplete_fields = ['empresa_ancla', 'director_proyecto']

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'empresa_ancla', 'descripcion')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin_planeada', 'fecha_fin_real')
        }),
        ('Estado', {
            'fields': ('estado', 'director_proyecto')
        }),
        ('Configuración', {
            'fields': (
                'numero_proveedores_planeado', 'duracion_meses',
                'horas_por_proveedor', 'presupuesto', 'costo_por_proveedor'
            )
        }),
        ('Detalles', {
            'fields': ('objetivos', 'alcance', 'notas'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProveedorProyectoInline, DocumentoProyectoInline]


@admin.register(ProveedorProyecto)
class ProveedorProyectoAdmin(admin.ModelAdmin):
    """Admin para ProveedorProyecto."""

    list_display = (
        'proveedor', 'proyecto', 'etapa_actual', 'estado',
        'consultor_asignado', 'porcentaje_avance', 'fecha_inicio'
    )
    list_filter = ('etapa_actual', 'estado', 'proyecto', 'consultor_asignado')
    search_fields = ('proveedor__razon_social', 'proyecto__nombre', 'proyecto__codigo')
    autocomplete_fields = ['proveedor', 'proyecto', 'consultor_asignado']


@admin.register(DocumentoProyecto)
class DocumentoProyectoAdmin(admin.ModelAdmin):
    """Admin para DocumentoProyecto."""

    list_display = ('proyecto', 'nombre', 'tipo', 'version', 'uploaded_at')
    list_filter = ('tipo', 'uploaded_at', 'proyecto')
    search_fields = ('nombre', 'proyecto__codigo')
    readonly_fields = ['uploaded_at', 'uploaded_by']
