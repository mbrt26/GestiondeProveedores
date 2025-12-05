from django.contrib import admin
from .models import Taller, SesionTaller, InscripcionTaller, AsistenciaTaller, CertificadoTaller, EvaluacionTaller


class SesionInline(admin.TabularInline):
    model = SesionTaller
    extra = 0


class InscripcionInline(admin.TabularInline):
    model = InscripcionTaller
    extra = 0


@admin.register(Taller)
class TallerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'modalidad', 'duracion_horas', 'facilitador', 'is_active')
    list_filter = ('tipo', 'modalidad', 'is_active')
    search_fields = ('nombre', 'descripcion')
    inlines = [SesionInline]


@admin.register(SesionTaller)
class SesionTallerAdmin(admin.ModelAdmin):
    list_display = ('taller', 'fecha', 'hora_inicio', 'lugar', 'estado', 'inscritos_count')
    list_filter = ('estado', 'fecha')
    search_fields = ('taller__nombre',)
    inlines = [InscripcionInline]


@admin.register(InscripcionTaller)
class InscripcionTallerAdmin(admin.ModelAdmin):
    list_display = ('participante_nombre', 'sesion', 'proveedor', 'estado', 'fecha_inscripcion')
    list_filter = ('estado', 'fecha_inscripcion')
    search_fields = ('participante_nombre', 'participante_email')


@admin.register(CertificadoTaller)
class CertificadoTallerAdmin(admin.ModelAdmin):
    list_display = ('codigo_certificado', 'inscripcion', 'fecha_emision', 'enviado')
    list_filter = ('enviado', 'fecha_emision')
