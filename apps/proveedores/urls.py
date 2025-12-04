from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    # CRUD Proveedores
    path('', views.ProveedorListView.as_view(), name='lista'),
    path('nuevo/', views.ProveedorCreateView.as_view(), name='crear'),
    path('<uuid:pk>/', views.ProveedorDetailView.as_view(), name='detalle'),
    path('<uuid:pk>/editar/', views.ProveedorUpdateView.as_view(), name='editar'),
    path('<uuid:pk>/eliminar/', views.ProveedorDeleteView.as_view(), name='eliminar'),

    # Vinculación con empresas ancla
    path('<uuid:pk>/vincular-empresa/', views.VincularEmpresaAnclaView.as_view(), name='vincular_empresa'),

    # Documentos
    path('<uuid:pk>/documentos/subir/', views.SubirDocumentoView.as_view(), name='subir_documento'),

    # Importación masiva
    path('importar/', views.ImportarProveedoresView.as_view(), name='importar'),
    path('importar/plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
]
