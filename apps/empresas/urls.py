from django.urls import path
from . import views

app_name = 'empresas'

urlpatterns = [
    # CRUD Empresas Ancla
    path('', views.EmpresaAnclaListView.as_view(), name='lista'),
    path('nueva/', views.EmpresaAnclaCreateView.as_view(), name='crear'),
    path('<uuid:pk>/', views.EmpresaAnclaDetailView.as_view(), name='detalle'),
    path('<uuid:pk>/editar/', views.EmpresaAnclaUpdateView.as_view(), name='editar'),
    path('<uuid:pk>/eliminar/', views.EmpresaAnclaDeleteView.as_view(), name='eliminar'),
    path('<uuid:pk>/toggle/', views.toggle_empresa_activa, name='toggle'),

    # Usuarios de empresa
    path('<uuid:empresa_pk>/usuarios/asignar/',
         views.UsuarioEmpresaAnclaCreateView.as_view(),
         name='usuario_asignar'),
]
