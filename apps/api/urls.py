"""
URLs para la API REST.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .viewsets import (
    UsuarioViewSet,
    EmpresaAnclaViewSet,
    ProveedorViewSet, DocumentoProveedorViewSet,
    ProyectoViewSet, ProveedorProyectoViewSet,
    Etapa1DiagnosticoViewSet, VozClienteViewSet, DiagnosticoCompetitividadViewSet,
    Etapa2PlanViewSet, HallazgoProblemaViewSet, AccionMejoraViewSet,
    Etapa3ImplementacionViewSet, TareaImplementacionViewSet,
    EvidenciaImplementacionViewSet, SesionAcompanamientoViewSet,
    Etapa4MonitoreoViewSet, IndicadorKPIViewSet, MedicionKPIViewSet, InformeCierreViewSet,
    TallerViewSet, SesionTallerViewSet, InscripcionTallerViewSet, AsistenciaTallerViewSet,
)

app_name = 'api'

# Crear router
router = DefaultRouter()

# Registrar viewsets
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'empresas', EmpresaAnclaViewSet, basename='empresa')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'documentos-proveedor', DocumentoProveedorViewSet, basename='documento-proveedor')
router.register(r'proyectos', ProyectoViewSet, basename='proyecto')
router.register(r'proveedores-proyecto', ProveedorProyectoViewSet, basename='proveedor-proyecto')

# Etapa 1 - Diagnóstico
router.register(r'etapa1/diagnosticos', Etapa1DiagnosticoViewSet, basename='etapa1-diagnostico')
router.register(r'etapa1/voz-cliente', VozClienteViewSet, basename='voz-cliente')
router.register(r'etapa1/competitividad', DiagnosticoCompetitividadViewSet, basename='competitividad')

# Etapa 2 - Plan
router.register(r'etapa2/planes', Etapa2PlanViewSet, basename='etapa2-plan')
router.register(r'etapa2/hallazgos', HallazgoProblemaViewSet, basename='hallazgo')
router.register(r'etapa2/acciones', AccionMejoraViewSet, basename='accion-mejora')

# Etapa 3 - Implementación
router.register(r'etapa3/implementaciones', Etapa3ImplementacionViewSet, basename='etapa3-implementacion')
router.register(r'etapa3/tareas', TareaImplementacionViewSet, basename='tarea')
router.register(r'etapa3/evidencias', EvidenciaImplementacionViewSet, basename='evidencia')
router.register(r'etapa3/sesiones', SesionAcompanamientoViewSet, basename='sesion-acompanamiento')

# Etapa 4 - Monitoreo
router.register(r'etapa4/monitoreos', Etapa4MonitoreoViewSet, basename='etapa4-monitoreo')
router.register(r'etapa4/kpis', IndicadorKPIViewSet, basename='kpi')
router.register(r'etapa4/mediciones', MedicionKPIViewSet, basename='medicion')
router.register(r'etapa4/informes', InformeCierreViewSet, basename='informe-cierre')

# Talleres
router.register(r'talleres', TallerViewSet, basename='taller')
router.register(r'sesiones-taller', SesionTallerViewSet, basename='sesion-taller')
router.register(r'inscripciones-taller', InscripcionTallerViewSet, basename='inscripcion-taller')
router.register(r'asistencias-taller', AsistenciaTallerViewSet, basename='asistencia-taller')

urlpatterns = [
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Router URLs
    path('', include(router.urls)),
]
