from django.urls import path
from . import views

app_name = 'etapas'

urlpatterns = [
    # Vista general de proveedor en proyecto
    path('proveedor/<uuid:pk>/', views.ProveedorProyectoEtapasView.as_view(), name='proveedor_etapas'),

    # Etapa 1: Diagnóstico
    path('proveedor/<uuid:pk>/etapa1/', views.Etapa1DetailView.as_view(), name='etapa1_detalle'),
    path('proveedor/<uuid:pk>/etapa1/voz-cliente/', views.VozClienteCreateView.as_view(), name='voz_cliente_crear'),
    path('proveedor/<uuid:pk>/etapa1/diagnostico/', views.DiagnosticoCreateView.as_view(), name='diagnostico_crear'),
    path('proveedor/<uuid:pk>/etapa1/objetivo/', views.ObjetivoCreateView.as_view(), name='objetivo_crear'),
    path('proveedor/<uuid:pk>/etapa1/documento/', views.DocumentoEtapa1CreateView.as_view(), name='documento_etapa1'),
    path('proveedor/<uuid:pk>/etapa1/completar/', views.completar_etapa1, name='completar_etapa1'),

    # Etapa 2: Plan
    path('proveedor/<uuid:pk>/etapa2/', views.Etapa2DetailView.as_view(), name='etapa2_detalle'),
    path('proveedor/<uuid:pk>/etapa2/hallazgo/', views.HallazgoCreateView.as_view(), name='hallazgo_crear'),
    path('hallazgo/<uuid:pk>/accion/', views.AccionMejoraCreateView.as_view(), name='accion_crear'),
    path('proveedor/<uuid:pk>/etapa2/cronograma/', views.CronogramaCreateView.as_view(), name='cronograma_crear'),
    path('proveedor/<uuid:pk>/etapa2/aprobar/', views.aprobar_plan, name='aprobar_plan'),

    # Etapa 3: Implementación
    path('proveedor/<uuid:pk>/etapa3/', views.Etapa3DetailView.as_view(), name='etapa3_detalle'),
    path('proveedor/<uuid:pk>/etapa3/tarea/', views.TareaCreateView.as_view(), name='tarea_crear'),
    path('tarea/<uuid:pk>/editar/', views.TareaUpdateView.as_view(), name='tarea_editar'),
    path('tarea/<uuid:pk>/estado/', views.cambiar_estado_tarea, name='tarea_cambiar_estado'),
    path('tarea/<uuid:pk>/evidencia/', views.EvidenciaCreateView.as_view(), name='evidencia_crear'),
    path('proveedor/<uuid:pk>/etapa3/sesion/', views.SesionCreateView.as_view(), name='sesion_crear'),
    path('proveedor/<uuid:pk>/etapa3/kanban/', views.kanban_data, name='kanban_data'),

    # Etapa 4: Monitoreo
    path('proveedor/<uuid:pk>/etapa4/', views.Etapa4DetailView.as_view(), name='etapa4_detalle'),
    path('proveedor/<uuid:pk>/etapa4/indicador/', views.IndicadorCreateView.as_view(), name='indicador_crear'),
    path('indicador/<uuid:pk>/medicion/', views.MedicionCreateView.as_view(), name='medicion_crear'),
    path('proveedor/<uuid:pk>/etapa4/reporte/', views.ReporteCreateView.as_view(), name='reporte_crear'),
    path('proveedor/<uuid:pk>/etapa4/evaluacion/', views.EvaluacionCreateView.as_view(), name='evaluacion_crear'),
    path('proveedor/<uuid:pk>/etapa4/informe-cierre/', views.generar_informe_cierre, name='informe_cierre'),
    path('proveedor/<uuid:pk>/etapa4/completar/', views.completar_etapa4, name='completar_etapa4'),
    path('proveedor/<uuid:pk>/etapa4/kpis-data/', views.kpis_chart_data, name='kpis_data'),
]
