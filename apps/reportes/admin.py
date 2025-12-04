from django.contrib import admin
from .models import ReporteGenerado, PlantillaReporte, ConfiguracionReporteAutomatico


@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'generado_por', 'fecha_generacion')
    list_filter = ('tipo', 'fecha_generacion')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_generacion',)


@admin.register(PlantillaReporte)
class PlantillaReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_reporte', 'is_active')
    list_filter = ('tipo_reporte', 'is_active')


@admin.register(ConfiguracionReporteAutomatico)
class ConfiguracionReporteAutomaticoAdmin(admin.ModelAdmin):
    list_display = ('empresa_ancla', 'tipo_reporte', 'frecuencia', 'is_active')
    list_filter = ('tipo_reporte', 'frecuencia', 'is_active')
