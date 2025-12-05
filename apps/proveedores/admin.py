from django.contrib import admin
from .models import Proveedor, ProveedorEmpresaAncla, DocumentoProveedor


class ProveedorEmpresaAnclaInline(admin.TabularInline):
    """Inline para vinculaciones con empresas ancla."""
    model = ProveedorEmpresaAncla
    extra = 1
    autocomplete_fields = ['empresa_ancla']


class DocumentoProveedorInline(admin.TabularInline):
    """Inline para documentos del proveedor."""
    model = DocumentoProveedor
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Admin para Proveedor."""

    list_display = (
        'razon_social', 'nit', 'ciudad', 'sector_economico',
        'tamano_empresa', 'numero_empleados'
    )
    list_filter = ('sector_economico', 'tamano_empresa', 'departamento', 'ciudad')
    search_fields = ('razon_social', 'nit', 'nombre_comercial', 'email')
    ordering = ('razon_social',)

    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'nit', 'nombre_comercial', 'logo')
        }),
        ('Representante Legal', {
            'fields': ('representante_legal', 'cedula_representante')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'celular', 'direccion', 'ciudad', 'departamento', 'codigo_postal')
        }),
        ('Información Empresarial', {
            'fields': (
                'sector_economico', 'actividad_economica', 'codigo_ciiu',
                'tamano_empresa', 'numero_empleados', 'anio_constitucion', 'sitio_web'
            )
        }),
        ('Información Financiera', {
            'fields': ('ventas_anuales', 'activos_totales'),
            'classes': ('collapse',)
        }),
        ('Contacto Adicional', {
            'fields': ('contacto_nombre', 'contacto_cargo', 'contacto_email', 'contacto_telefono'),
            'classes': ('collapse',)
        }),
        ('Descripción', {
            'fields': ('descripcion', 'productos_servicios'),
            'classes': ('collapse',)
        }),
        ('Documentos Básicos', {
            'fields': ('rut', 'camara_comercio'),
            'classes': ('collapse',)
        }),
        ('Acceso al Sistema', {
            'fields': ('usuario',),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProveedorEmpresaAnclaInline, DocumentoProveedorInline]


@admin.register(ProveedorEmpresaAncla)
class ProveedorEmpresaAnclaAdmin(admin.ModelAdmin):
    """Admin para ProveedorEmpresaAncla."""

    list_display = ('proveedor', 'empresa_ancla', 'estado', 'categoria', 'fecha_vinculacion')
    list_filter = ('estado', 'empresa_ancla', 'fecha_vinculacion')
    search_fields = ('proveedor__razon_social', 'empresa_ancla__nombre')
    autocomplete_fields = ['proveedor', 'empresa_ancla']


@admin.register(DocumentoProveedor)
class DocumentoProveedorAdmin(admin.ModelAdmin):
    """Admin para DocumentoProveedor."""

    list_display = ('proveedor', 'nombre', 'tipo', 'fecha_vencimiento', 'uploaded_at')
    list_filter = ('tipo', 'uploaded_at')
    search_fields = ('proveedor__razon_social', 'nombre')
    readonly_fields = ['uploaded_at', 'uploaded_by']
