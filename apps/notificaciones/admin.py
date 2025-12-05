from django.contrib import admin
from .models import (
    PlantillaNotificacion, Notificacion, ConfiguracionNotificacion,
    ColaNotificacion, ConfiguracionEmail, ConfiguracionWhatsApp, HistorialEnvio
)


@admin.register(PlantillaNotificacion)
class PlantillaNotificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'evento', 'tipo', 'is_active')
    list_filter = ('tipo', 'evento', 'is_active')
    search_fields = ('nombre', 'asunto')


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'estado', 'created_at')
    list_filter = ('tipo', 'estado', 'created_at')
    search_fields = ('titulo', 'usuario__email')
    readonly_fields = ('created_at', 'fecha_envio', 'fecha_lectura')


@admin.register(ConfiguracionNotificacion)
class ConfiguracionNotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'email_activo', 'whatsapp_activo', 'sistema_activo')
    list_filter = ('email_activo', 'whatsapp_activo', 'sistema_activo')


@admin.register(ColaNotificacion)
class ColaNotificacionAdmin(admin.ModelAdmin):
    list_display = ('notificacion', 'prioridad', 'procesado', 'created_at')
    list_filter = ('prioridad', 'procesado')


@admin.register(ConfiguracionEmail)
class ConfiguracionEmailAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email_remitente', 'is_active')
    list_filter = ('is_active',)


@admin.register(ConfiguracionWhatsApp)
class ConfiguracionWhatsAppAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'numero_telefono', 'is_active')
    list_filter = ('is_active',)


@admin.register(HistorialEnvio)
class HistorialEnvioAdmin(admin.ModelAdmin):
    list_display = ('notificacion', 'canal', 'destinatario', 'exitoso', 'fecha_envio')
    list_filter = ('canal', 'exitoso', 'fecha_envio')
    readonly_fields = ('fecha_envio',)
