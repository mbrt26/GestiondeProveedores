from django.contrib import admin
from .models import EmpresaAncla, UsuarioEmpresaAncla


class UsuarioEmpresaAnclaInline(admin.TabularInline):
    """Inline para usuarios de empresa ancla."""
    model = UsuarioEmpresaAncla
    extra = 1
    autocomplete_fields = ['usuario']


@admin.register(EmpresaAncla)
class EmpresaAnclaAdmin(admin.ModelAdmin):
    """Admin para EmpresaAncla."""

    list_display = ('nombre', 'nit', 'sector_economico', 'ciudad', 'proyectos_activos', 'is_active')
    list_filter = ('sector_economico', 'is_active', 'ciudad', 'departamento')
    search_fields = ('nombre', 'nit', 'razon_social', 'email')
    ordering = ('nombre',)

    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nit', 'razon_social', 'logo')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'departamento', 'pais')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'sitio_web')
        }),
        ('Información Empresarial', {
            'fields': ('sector_economico', 'descripcion', 'numero_empleados', 'anio_fundacion')
        }),
        ('Contacto Principal', {
            'fields': ('contacto_nombre', 'contacto_cargo', 'contacto_email', 'contacto_telefono'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('configuracion', 'notas', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    inlines = [UsuarioEmpresaAnclaInline]


@admin.register(UsuarioEmpresaAncla)
class UsuarioEmpresaAnclaAdmin(admin.ModelAdmin):
    """Admin para UsuarioEmpresaAncla."""

    list_display = ('usuario', 'empresa_ancla', 'rol', 'is_active', 'created_at')
    list_filter = ('rol', 'is_active', 'empresa_ancla')
    search_fields = ('usuario__email', 'usuario__nombre', 'empresa_ancla__nombre')
    autocomplete_fields = ['usuario', 'empresa_ancla']
