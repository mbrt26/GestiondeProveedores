from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReporteListView.as_view(), name='lista'),
    path('generar/avance-proveedor/<uuid:pk>/', views.generar_reporte_proveedor, name='avance_proveedor'),
    path('generar/consolidado-proyecto/<uuid:pk>/', views.generar_reporte_proyecto, name='consolidado_proyecto'),
    path('generar/ejecutivo/<uuid:pk>/', views.generar_reporte_ejecutivo, name='ejecutivo'),
    path('descargar/<uuid:pk>/', views.descargar_reporte, name='descargar'),
]
