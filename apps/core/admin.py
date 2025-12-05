from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Usuario, ConfiguracionSistema, LogActividad


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin para el modelo Usuario personalizado."""

    list_display = ('email', 'nombre', 'apellido', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'telefono', 'cargo', 'avatar')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'rol', 'password1', 'password2'),
        }),
    )


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """Admin para ConfiguracionSistema."""

    list_display = ('clave', 'valor_truncado', 'tipo', 'is_active', 'updated_at')
    list_filter = ('tipo', 'is_active')
    search_fields = ('clave', 'descripcion')
    ordering = ('clave',)

    def valor_truncado(self, obj):
        if len(obj.valor) > 50:
            return obj.valor[:50] + '...'
        return obj.valor
    valor_truncado.short_description = 'Valor'


@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    """Admin para LogActividad."""

    list_display = ('usuario', 'accion', 'modelo', 'descripcion_truncada', 'ip_address', 'created_at')
    list_filter = ('accion', 'modelo', 'created_at')
    search_fields = ('usuario__email', 'descripcion', 'modelo')
    readonly_fields = ('id', 'usuario', 'accion', 'modelo', 'objeto_id', 'descripcion',
                       'datos_anteriores', 'datos_nuevos', 'ip_address', 'user_agent', 'created_at')
    ordering = ('-created_at',)

    def descripcion_truncada(self, obj):
        if len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_truncada.short_description = 'Descripción'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Personalización del Admin Site
admin.site.site_header = 'Sistema de Fortalecimiento de Proveedores'
admin.site.site_title = 'SFP Admin'
admin.site.index_title = 'Panel de Administración'
