from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    # CRUD Proyectos
    path('', views.ProyectoListView.as_view(), name='lista'),
    path('nuevo/', views.ProyectoCreateView.as_view(), name='crear'),
    path('<uuid:pk>/', views.ProyectoDetailView.as_view(), name='detalle'),
    path('<uuid:pk>/editar/', views.ProyectoUpdateView.as_view(), name='editar'),
    path('<uuid:pk>/eliminar/', views.ProyectoDeleteView.as_view(), name='eliminar'),

    # Gestión de proveedores en proyecto
    path('<uuid:pk>/proveedores/asignar/', views.AsignarProveedorView.as_view(), name='asignar_proveedor'),
    path('<uuid:pk>/proveedores/asignar-multiples/', views.AsignarMultiplesProveedoresView.as_view(), name='asignar_multiples'),
    path('<uuid:pk>/proveedores/<uuid:proveedor_pk>/remover/', views.RemoverProveedorView.as_view(), name='remover_proveedor'),
    path('<uuid:pk>/proveedores/<uuid:proveedor_pk>/cambiar-consultor/', views.CambiarConsultorView.as_view(), name='cambiar_consultor'),
    path('<uuid:pk>/proveedores/<uuid:proveedor_pk>/iniciar/', views.iniciar_proveedor, name='iniciar_proveedor'),

    # Documentos
    path('<uuid:pk>/documentos/subir/', views.SubirDocumentoProyectoView.as_view(), name='subir_documento'),

    # API
    path('<uuid:pk>/dashboard-data/', views.proyecto_dashboard_data, name='dashboard_data'),
]
