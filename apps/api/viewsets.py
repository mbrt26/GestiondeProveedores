"""
ViewSets para la API REST.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.models import Usuario
from apps.empresas.models import EmpresaAncla
from apps.proveedores.models import Proveedor, DocumentoProveedor
from apps.proyectos.models import Proyecto, ProveedorProyecto
from apps.etapas.models import (
    Etapa1Diagnostico, VozCliente, DiagnosticoCompetitividad, ObjetivoFortalecimiento,
    Etapa2Plan, HallazgoProblema, AccionMejora,
    Etapa3Implementacion, TareaImplementacion, EvidenciaImplementacion, SesionAcompanamiento,
    Etapa4Monitoreo, IndicadorKPI, MedicionKPI, InformeCierre
)
from apps.talleres.models import Taller, SesionTaller, InscripcionTaller, AsistenciaTaller

from .serializers import (
    UsuarioSerializer, UsuarioCreateSerializer,
    EmpresaAnclaSerializer, EmpresaAnclaListSerializer,
    ProveedorSerializer, ProveedorListSerializer, DocumentoProveedorSerializer,
    ProyectoSerializer, ProyectoListSerializer, ProveedorProyectoSerializer,
    Etapa1DiagnosticoSerializer, VozClienteSerializer, DiagnosticoCompetitividadSerializer,
    ObjetivoFortalecimientoSerializer, Etapa2PlanSerializer, HallazgoProblemaSerializer,
    AccionMejoraSerializer, Etapa3ImplementacionSerializer, TareaImplementacionSerializer,
    EvidenciaImplementacionSerializer, SesionAcompanamientoSerializer,
    Etapa4MonitoreoSerializer, IndicadorKPISerializer, MedicionKPISerializer,
    InformeCierreSerializer, TallerSerializer, TallerListSerializer,
    SesionTallerSerializer, InscripcionTallerSerializer, AsistenciaTallerSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, EmpresaAnclaPermission


# =====================
# Core ViewSets
# =====================

class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios."""
    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rol', 'is_active']
    search_fields = ['email', 'nombre', 'apellido']
    ordering_fields = ['date_joined', 'nombre', 'apellido']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Actualizar perfil del usuario actual."""
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# =====================
# Empresas ViewSets
# =====================

class EmpresaAnclaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de Empresas Ancla."""
    queryset = EmpresaAncla.objects.all()
    permission_classes = [IsAuthenticated, EmpresaAnclaPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sector', 'is_active']
    search_fields = ['nit', 'razon_social', 'nombre_comercial']
    ordering_fields = ['razon_social', 'fecha_vinculacion']
    ordering = ['razon_social']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpresaAnclaListSerializer
        return EmpresaAnclaSerializer

    def get_queryset(self):
        """Filtrar empresas según rol del usuario."""
        user = self.request.user
        if user.rol == 'ADMIN':
            return EmpresaAncla.objects.all()
        return EmpresaAncla.objects.filter(
            usuarios_empresa__usuario=user
        ).distinct()

    @action(detail=True, methods=['get'])
    def proveedores(self, request, pk=None):
        """Listar proveedores de la empresa."""
        empresa = self.get_object()
        proveedores = Proveedor.objects.filter(
            proveedores_empresa__empresa_ancla=empresa,
            proveedores_empresa__is_active=True
        )
        serializer = ProveedorListSerializer(proveedores, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def proyectos(self, request, pk=None):
        """Listar proyectos de la empresa."""
        empresa = self.get_object()
        proyectos = empresa.proyectos.all()
        serializer = ProyectoListSerializer(proyectos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Dashboard de la empresa."""
        empresa = self.get_object()

        # Estadísticas
        proveedores_activos = empresa.proveedores_empresa.filter(is_active=True).count()
        proyectos_activos = empresa.proyectos.filter(estado='EN_CURSO').count()
        proyectos_finalizados = empresa.proyectos.filter(estado='FINALIZADO').count()

        # Distribución por etapas
        distribucion = {}
        for proyecto in empresa.proyectos.filter(estado='EN_CURSO'):
            for pp in proyecto.proveedores_proyecto.all():
                etapa = pp.get_etapa_actual_display()
                distribucion[etapa] = distribucion.get(etapa, 0) + 1

        return Response({
            'empresa': EmpresaAnclaSerializer(empresa).data,
            'total_proveedores': proveedores_activos,
            'proyectos_activos': proyectos_activos,
            'proyectos_finalizados': proyectos_finalizados,
            'distribucion_etapas': distribucion
        })


# =====================
# Proveedores ViewSets
# =====================

class ProveedorViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de Proveedores."""
    queryset = Proveedor.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sector', 'tamano', 'ciudad', 'is_active']
    search_fields = ['nit', 'razon_social', 'nombre_comercial']
    ordering_fields = ['razon_social', 'fecha_registro']
    ordering = ['razon_social']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProveedorListSerializer
        return ProveedorSerializer

    def get_queryset(self):
        """Filtrar proveedores según rol del usuario."""
        user = self.request.user
        if user.rol == 'ADMIN':
            return Proveedor.objects.all()
        elif user.rol == 'EMPRESA_ANCLA':
            return Proveedor.objects.filter(
                proveedores_empresa__empresa_ancla__usuarios_empresa__usuario=user
            ).distinct()
        elif user.rol == 'PROVEEDOR':
            return Proveedor.objects.filter(usuario_principal=user)
        return Proveedor.objects.none()

    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        """Listar documentos del proveedor."""
        proveedor = self.get_object()
        documentos = proveedor.documentos.all()
        serializer = DocumentoProveedorSerializer(documentos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def proyectos(self, request, pk=None):
        """Listar proyectos del proveedor."""
        proveedor = self.get_object()
        proyectos_proveedor = ProveedorProyecto.objects.filter(
            proveedor=proveedor
        ).select_related('proyecto')
        serializer = ProveedorProyectoSerializer(proyectos_proveedor, many=True)
        return Response(serializer.data)


class DocumentoProveedorViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de documentos de proveedores."""
    queryset = DocumentoProveedor.objects.all()
    serializer_class = DocumentoProveedorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['proveedor', 'tipo', 'verificado']


# =====================
# Proyectos ViewSets
# =====================

class ProyectoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de Proyectos."""
    queryset = Proyecto.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa_ancla', 'estado', 'consultor_lider']
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['fecha_inicio', 'nombre', 'created_at']
    ordering = ['-fecha_inicio']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProyectoListSerializer
        return ProyectoSerializer

    def get_queryset(self):
        """Filtrar proyectos según rol del usuario."""
        user = self.request.user
        if user.rol == 'ADMIN':
            return Proyecto.objects.all()
        elif user.rol == 'EMPRESA_ANCLA':
            return Proyecto.objects.filter(
                empresa_ancla__usuarios_empresa__usuario=user
            ).distinct()
        elif user.rol == 'CONSULTOR':
            return Proyecto.objects.filter(consultor_lider=user)
        elif user.rol == 'PROVEEDOR':
            return Proyecto.objects.filter(
                proveedores_proyecto__proveedor__usuario_principal=user
            ).distinct()
        return Proyecto.objects.none()

    @action(detail=True, methods=['get'])
    def proveedores(self, request, pk=None):
        """Listar proveedores del proyecto."""
        proyecto = self.get_object()
        proveedores_proyecto = proyecto.proveedores_proyecto.all()
        serializer = ProveedorProyectoSerializer(proveedores_proyecto, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Dashboard del proyecto."""
        proyecto = self.get_object()

        # Distribución por etapas
        proveedores_por_etapa = {
            'Etapa 1': proyecto.proveedores_proyecto.filter(etapa_actual=1).count(),
            'Etapa 2': proyecto.proveedores_proyecto.filter(etapa_actual=2).count(),
            'Etapa 3': proyecto.proveedores_proyecto.filter(etapa_actual=3).count(),
            'Etapa 4': proyecto.proveedores_proyecto.filter(etapa_actual=4).count(),
        }

        # Tareas pendientes
        tareas_pendientes = TareaImplementacion.objects.filter(
            implementacion__proveedor_proyecto__proyecto=proyecto,
            estado__in=['PENDIENTE', 'EN_PROGRESO']
        ).count()

        return Response({
            'proyecto': ProyectoSerializer(proyecto).data,
            'proveedores_por_etapa': proveedores_por_etapa,
            'tareas_pendientes': tareas_pendientes,
            'total_proveedores': proyecto.proveedores_proyecto.count()
        })


class ProveedorProyectoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de Proveedores en Proyectos."""
    queryset = ProveedorProyecto.objects.all()
    serializer_class = ProveedorProyectoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['proyecto', 'proveedor', 'etapa_actual', 'estado']
    ordering = ['proveedor__razon_social']

    @action(detail=True, methods=['post'])
    def avanzar_etapa(self, request, pk=None):
        """Avanzar a la siguiente etapa."""
        proveedor_proyecto = self.get_object()

        if proveedor_proyecto.puede_avanzar_etapa():
            etapa_anterior = proveedor_proyecto.etapa_actual
            proveedor_proyecto.avanzar_etapa()
            return Response({
                'success': True,
                'etapa_anterior': etapa_anterior,
                'etapa_actual': proveedor_proyecto.etapa_actual,
                'mensaje': f'Avanzado a {proveedor_proyecto.get_etapa_actual_display()}'
            })
        return Response({
            'success': False,
            'mensaje': 'No es posible avanzar de etapa. Verifique el progreso actual.'
        }, status=status.HTTP_400_BAD_REQUEST)


# =====================
# Etapas ViewSets
# =====================

class Etapa1DiagnosticoViewSet(viewsets.ModelViewSet):
    """ViewSet para Etapa 1 - Diagnóstico."""
    queryset = Etapa1Diagnostico.objects.all()
    serializer_class = Etapa1DiagnosticoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['proveedor_proyecto', 'estado']


class VozClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para Voz del Cliente."""
    queryset = VozCliente.objects.all()
    serializer_class = VozClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['diagnostico', 'categoria']


class DiagnosticoCompetitividadViewSet(viewsets.ModelViewSet):
    """ViewSet para Diagnóstico de Competitividad."""
    queryset = DiagnosticoCompetitividad.objects.all()
    serializer_class = DiagnosticoCompetitividadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['diagnostico', 'dimension', 'estado']


class Etapa2PlanViewSet(viewsets.ModelViewSet):
    """ViewSet para Etapa 2 - Plan."""
    queryset = Etapa2Plan.objects.all()
    serializer_class = Etapa2PlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['proveedor_proyecto', 'estado']


class HallazgoProblemaViewSet(viewsets.ModelViewSet):
    """ViewSet para Hallazgos/Problemas."""
    queryset = HallazgoProblema.objects.all()
    serializer_class = HallazgoProblemaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['plan', 'tipo', 'criticidad']


class AccionMejoraViewSet(viewsets.ModelViewSet):
    """ViewSet para Acciones de Mejora."""
    queryset = AccionMejora.objects.all()
    serializer_class = AccionMejoraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hallazgo', 'prioridad', 'estado']


class Etapa3ImplementacionViewSet(viewsets.ModelViewSet):
    """ViewSet para Etapa 3 - Implementación."""
    queryset = Etapa3Implementacion.objects.all()
    serializer_class = Etapa3ImplementacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['proveedor_proyecto', 'estado']


class TareaImplementacionViewSet(viewsets.ModelViewSet):
    """ViewSet para Tareas de Implementación."""
    queryset = TareaImplementacion.objects.all()
    serializer_class = TareaImplementacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['implementacion', 'responsable', 'estado', 'prioridad']
    search_fields = ['titulo']
    ordering_fields = ['fecha_limite', 'prioridad', 'created_at']
    ordering = ['fecha_limite']

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de la tarea."""
        tarea = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(TareaImplementacion.Estado.choices):
            return Response({
                'error': 'Estado no válido'
            }, status=status.HTTP_400_BAD_REQUEST)

        tarea.estado = nuevo_estado
        tarea.save()

        return Response({
            'success': True,
            'estado': tarea.estado
        })


class EvidenciaImplementacionViewSet(viewsets.ModelViewSet):
    """ViewSet para Evidencias de Implementación."""
    queryset = EvidenciaImplementacion.objects.all()
    serializer_class = EvidenciaImplementacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tarea', 'tipo']


class SesionAcompanamientoViewSet(viewsets.ModelViewSet):
    """ViewSet para Sesiones de Acompañamiento."""
    queryset = SesionAcompanamiento.objects.all()
    serializer_class = SesionAcompanamientoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['implementacion', 'tipo', 'estado']
    ordering = ['-fecha_programada']


class Etapa4MonitoreoViewSet(viewsets.ModelViewSet):
    """ViewSet para Etapa 4 - Monitoreo."""
    queryset = Etapa4Monitoreo.objects.all()
    serializer_class = Etapa4MonitoreoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['proveedor_proyecto', 'estado']


class IndicadorKPIViewSet(viewsets.ModelViewSet):
    """ViewSet para Indicadores KPI."""
    queryset = IndicadorKPI.objects.all()
    serializer_class = IndicadorKPISerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['monitoreo', 'categoria', 'is_active']
    search_fields = ['nombre', 'descripcion']


class MedicionKPIViewSet(viewsets.ModelViewSet):
    """ViewSet para Mediciones KPI."""
    queryset = MedicionKPI.objects.all()
    serializer_class = MedicionKPISerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['indicador', 'periodo']
    ordering = ['-fecha_medicion']


class InformeCierreViewSet(viewsets.ModelViewSet):
    """ViewSet para Informes de Cierre."""
    queryset = InformeCierre.objects.all()
    serializer_class = InformeCierreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['monitoreo', 'estado']


# =====================
# Talleres ViewSets
# =====================

class TallerViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de Talleres."""
    queryset = Taller.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proyecto', 'tipo', 'modalidad', 'estado']
    search_fields = ['nombre']
    ordering_fields = ['fecha_inicio', 'nombre']
    ordering = ['-fecha_inicio']

    def get_serializer_class(self):
        if self.action == 'list':
            return TallerListSerializer
        return TallerSerializer

    @action(detail=True, methods=['get'])
    def sesiones(self, request, pk=None):
        """Listar sesiones del taller."""
        taller = self.get_object()
        sesiones = taller.sesiones.all()
        serializer = SesionTallerSerializer(sesiones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def inscritos(self, request, pk=None):
        """Listar inscritos al taller."""
        taller = self.get_object()
        inscripciones = taller.inscripciones.all()
        serializer = InscripcionTallerSerializer(inscripciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def inscribir(self, request, pk=None):
        """Inscribir usuario al taller."""
        taller = self.get_object()
        usuario = request.user

        # Verificar cupo
        inscritos = taller.inscripciones.filter(estado='CONFIRMADA').count()
        if inscritos >= taller.cupo_maximo:
            return Response({
                'error': 'El taller está lleno'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya está inscrito
        if taller.inscripciones.filter(usuario=usuario).exists():
            return Response({
                'error': 'Ya está inscrito en este taller'
            }, status=status.HTTP_400_BAD_REQUEST)

        inscripcion = InscripcionTaller.objects.create(
            taller=taller,
            usuario=usuario,
            estado='CONFIRMADA'
        )

        return Response({
            'success': True,
            'inscripcion': InscripcionTallerSerializer(inscripcion).data
        })


class SesionTallerViewSet(viewsets.ModelViewSet):
    """ViewSet para sesiones de taller."""
    queryset = SesionTaller.objects.all()
    serializer_class = SesionTallerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['taller', 'estado']
    ordering = ['fecha']


class InscripcionTallerViewSet(viewsets.ModelViewSet):
    """ViewSet para inscripciones a talleres."""
    queryset = InscripcionTaller.objects.all()
    serializer_class = InscripcionTallerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['taller', 'usuario', 'estado']


class AsistenciaTallerViewSet(viewsets.ModelViewSet):
    """ViewSet para asistencia a talleres."""
    queryset = AsistenciaTaller.objects.all()
    serializer_class = AsistenciaTallerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sesion', 'inscripcion', 'presente']
