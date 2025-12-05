"""
Serializadores para la API REST.
"""
from rest_framework import serializers
from apps.core.models import Usuario
from apps.empresas.models import EmpresaAncla, UsuarioEmpresaAncla
from apps.proveedores.models import Proveedor, ProveedorEmpresaAncla, DocumentoProveedor
from apps.proyectos.models import Proyecto, ProveedorProyecto, DocumentoProyecto
from apps.etapas.models import (
    Etapa1Diagnostico, VozCliente, DiagnosticoCompetitividad, ObjetivoFortalecimiento,
    Etapa2Plan, HallazgoProblema, AccionMejora, CronogramaImplementacion,
    Etapa3Implementacion, TareaImplementacion, EvidenciaImplementacion, SesionAcompanamiento,
    Etapa4Monitoreo, IndicadorKPI, MedicionKPI, ReporteSemanal, InformeCierre
)
from apps.talleres.models import Taller, SesionTaller, InscripcionTaller, AsistenciaTaller


# =====================
# Core Serializers
# =====================

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador para Usuario."""
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre', 'apellido', 'nombre_completo',
            'rol', 'telefono', 'cargo', 'foto', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear Usuario."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'apellido', 'rol', 'telefono', 'cargo', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


# =====================
# Empresas Serializers
# =====================

class EmpresaAnclaSerializer(serializers.ModelSerializer):
    """Serializador para Empresa Ancla."""
    total_proveedores = serializers.SerializerMethodField()
    proyectos_activos = serializers.SerializerMethodField()

    class Meta:
        model = EmpresaAncla
        fields = [
            'id', 'nit', 'razon_social', 'nombre_comercial', 'sector',
            'direccion', 'ciudad', 'telefono', 'email', 'sitio_web',
            'logo', 'is_active', 'fecha_vinculacion',
            'total_proveedores', 'proyectos_activos'
        ]
        read_only_fields = ['id', 'fecha_vinculacion']

    def get_total_proveedores(self, obj):
        return obj.proveedores_empresa.filter(is_active=True).count()

    def get_proyectos_activos(self, obj):
        return obj.proyectos.filter(estado='EN_CURSO').count()


class EmpresaAnclaListSerializer(serializers.ModelSerializer):
    """Serializador resumido para lista de Empresas Ancla."""

    class Meta:
        model = EmpresaAncla
        fields = ['id', 'nit', 'razon_social', 'nombre_comercial', 'sector', 'is_active']


# =====================
# Proveedores Serializers
# =====================

class ProveedorSerializer(serializers.ModelSerializer):
    """Serializador para Proveedor."""
    usuario_principal_email = serializers.EmailField(
        source='usuario_principal.email', read_only=True
    )

    class Meta:
        model = Proveedor
        fields = [
            'id', 'nit', 'razon_social', 'nombre_comercial', 'tipo_empresa',
            'sector', 'tamano', 'direccion', 'ciudad', 'departamento',
            'telefono', 'email', 'sitio_web', 'numero_empleados',
            'ventas_anuales', 'logo', 'descripcion', 'usuario_principal',
            'usuario_principal_email', 'is_active', 'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']


class ProveedorListSerializer(serializers.ModelSerializer):
    """Serializador resumido para lista de Proveedores."""

    class Meta:
        model = Proveedor
        fields = ['id', 'nit', 'razon_social', 'sector', 'tamano', 'ciudad', 'is_active']


class DocumentoProveedorSerializer(serializers.ModelSerializer):
    """Serializador para Documento de Proveedor."""

    class Meta:
        model = DocumentoProveedor
        fields = ['id', 'proveedor', 'tipo', 'nombre', 'archivo', 'fecha_vencimiento', 'verificado', 'created_at']
        read_only_fields = ['id', 'created_at']


# =====================
# Proyectos Serializers
# =====================

class ProyectoSerializer(serializers.ModelSerializer):
    """Serializador para Proyecto."""
    empresa_ancla_nombre = serializers.CharField(
        source='empresa_ancla.razon_social', read_only=True
    )
    consultor_nombre = serializers.CharField(
        source='consultor_lider.get_full_name', read_only=True
    )
    total_proveedores = serializers.SerializerMethodField()
    progreso_general = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'empresa_ancla',
            'empresa_ancla_nombre', 'consultor_lider', 'consultor_nombre',
            'fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real',
            'estado', 'presupuesto', 'total_proveedores', 'progreso_general',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'codigo', 'created_at', 'updated_at']

    def get_total_proveedores(self, obj):
        return obj.proveedores_proyecto.count()

    def get_progreso_general(self, obj):
        proveedores = obj.proveedores_proyecto.all()
        if not proveedores:
            return 0
        total_progreso = sum(p.progreso_general for p in proveedores)
        return round(total_progreso / proveedores.count(), 2)


class ProyectoListSerializer(serializers.ModelSerializer):
    """Serializador resumido para lista de Proyectos."""
    empresa_ancla_nombre = serializers.CharField(
        source='empresa_ancla.razon_social', read_only=True
    )

    class Meta:
        model = Proyecto
        fields = ['id', 'codigo', 'nombre', 'empresa_ancla_nombre', 'estado', 'fecha_inicio', 'fecha_fin_estimada']


class ProveedorProyectoSerializer(serializers.ModelSerializer):
    """Serializador para Proveedor en Proyecto."""
    proveedor_nombre = serializers.CharField(
        source='proveedor.razon_social', read_only=True
    )
    proyecto_nombre = serializers.CharField(
        source='proyecto.nombre', read_only=True
    )
    etapa_display = serializers.CharField(
        source='get_etapa_actual_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )

    class Meta:
        model = ProveedorProyecto
        fields = [
            'id', 'proyecto', 'proyecto_nombre', 'proveedor', 'proveedor_nombre',
            'consultor_asignado', 'etapa_actual', 'etapa_display', 'estado',
            'estado_display', 'fecha_inicio', 'fecha_fin', 'progreso_general',
            'progreso_etapa1', 'progreso_etapa2', 'progreso_etapa3', 'progreso_etapa4',
            'observaciones'
        ]
        read_only_fields = ['id', 'fecha_inicio', 'progreso_general']


# =====================
# Etapas Serializers
# =====================

class Etapa1DiagnosticoSerializer(serializers.ModelSerializer):
    """Serializador para Etapa 1 - Diagnóstico."""

    class Meta:
        model = Etapa1Diagnostico
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class VozClienteSerializer(serializers.ModelSerializer):
    """Serializador para Voz del Cliente."""

    class Meta:
        model = VozCliente
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DiagnosticoCompetitividadSerializer(serializers.ModelSerializer):
    """Serializador para Diagnóstico de Competitividad."""

    class Meta:
        model = DiagnosticoCompetitividad
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ObjetivoFortalecimientoSerializer(serializers.ModelSerializer):
    """Serializador para Objetivo de Fortalecimiento."""

    class Meta:
        model = ObjetivoFortalecimiento
        fields = '__all__'
        read_only_fields = ['id']


class Etapa2PlanSerializer(serializers.ModelSerializer):
    """Serializador para Etapa 2 - Plan."""

    class Meta:
        model = Etapa2Plan
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class HallazgoProblemaSerializer(serializers.ModelSerializer):
    """Serializador para Hallazgo/Problema."""

    class Meta:
        model = HallazgoProblema
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AccionMejoraSerializer(serializers.ModelSerializer):
    """Serializador para Acción de Mejora."""

    class Meta:
        model = AccionMejora
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class Etapa3ImplementacionSerializer(serializers.ModelSerializer):
    """Serializador para Etapa 3 - Implementación."""

    class Meta:
        model = Etapa3Implementacion
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TareaImplementacionSerializer(serializers.ModelSerializer):
    """Serializador para Tarea de Implementación."""
    responsable_nombre = serializers.CharField(
        source='responsable.get_full_name', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )

    class Meta:
        model = TareaImplementacion
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class EvidenciaImplementacionSerializer(serializers.ModelSerializer):
    """Serializador para Evidencia de Implementación."""

    class Meta:
        model = EvidenciaImplementacion
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class SesionAcompanamientoSerializer(serializers.ModelSerializer):
    """Serializador para Sesión de Acompañamiento."""

    class Meta:
        model = SesionAcompanamiento
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class Etapa4MonitoreoSerializer(serializers.ModelSerializer):
    """Serializador para Etapa 4 - Monitoreo."""

    class Meta:
        model = Etapa4Monitoreo
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class IndicadorKPISerializer(serializers.ModelSerializer):
    """Serializador para Indicador KPI."""

    class Meta:
        model = IndicadorKPI
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MedicionKPISerializer(serializers.ModelSerializer):
    """Serializador para Medición KPI."""

    class Meta:
        model = MedicionKPI
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class InformeCierreSerializer(serializers.ModelSerializer):
    """Serializador para Informe de Cierre."""

    class Meta:
        model = InformeCierre
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# =====================
# Talleres Serializers
# =====================

class TallerSerializer(serializers.ModelSerializer):
    """Serializador para Taller."""
    inscritos_count = serializers.SerializerMethodField()

    class Meta:
        model = Taller
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_inscritos_count(self, obj):
        return obj.inscripciones.filter(estado='CONFIRMADA').count()


class TallerListSerializer(serializers.ModelSerializer):
    """Serializador resumido para lista de Talleres."""

    class Meta:
        model = Taller
        fields = ['id', 'nombre', 'tipo', 'modalidad', 'cupo_maximo', 'estado', 'fecha_inicio']


class SesionTallerSerializer(serializers.ModelSerializer):
    """Serializador para Sesión de Taller."""

    class Meta:
        model = SesionTaller
        fields = '__all__'
        read_only_fields = ['id']


class InscripcionTallerSerializer(serializers.ModelSerializer):
    """Serializador para Inscripción a Taller."""
    usuario_nombre = serializers.CharField(
        source='usuario.get_full_name', read_only=True
    )
    taller_nombre = serializers.CharField(
        source='taller.nombre', read_only=True
    )

    class Meta:
        model = InscripcionTaller
        fields = '__all__'
        read_only_fields = ['id', 'fecha_inscripcion']


class AsistenciaTallerSerializer(serializers.ModelSerializer):
    """Serializador para Asistencia a Taller."""

    class Meta:
        model = AsistenciaTaller
        fields = '__all__'
        read_only_fields = ['id']


# =====================
# Dashboard Serializers
# =====================

class DashboardEmpresaSerializer(serializers.Serializer):
    """Serializador para dashboard de Empresa Ancla."""
    empresa = EmpresaAnclaSerializer()
    total_proveedores = serializers.IntegerField()
    proveedores_activos = serializers.IntegerField()
    proyectos_activos = serializers.IntegerField()
    proyectos_finalizados = serializers.IntegerField()
    progreso_promedio = serializers.FloatField()
    distribucion_etapas = serializers.DictField()
    kpis_resumen = serializers.ListField()


class DashboardProyectoSerializer(serializers.Serializer):
    """Serializador para dashboard de Proyecto."""
    proyecto = ProyectoSerializer()
    proveedores_por_etapa = serializers.DictField()
    progreso_general = serializers.FloatField()
    tareas_pendientes = serializers.IntegerField()
    sesiones_programadas = serializers.IntegerField()
    alertas = serializers.ListField()


class DashboardProveedorSerializer(serializers.Serializer):
    """Serializador para dashboard de Proveedor."""
    proveedor = ProveedorSerializer()
    proyectos_activos = serializers.ListField()
    etapa_actual = serializers.CharField()
    progreso = serializers.FloatField()
    tareas_pendientes = serializers.IntegerField()
    proximas_sesiones = serializers.ListField()
    kpis = serializers.ListField()
