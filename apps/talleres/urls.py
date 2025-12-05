from django.urls import path
from . import views

app_name = 'talleres'

urlpatterns = [
    path('', views.TallerListView.as_view(), name='lista'),
    path('nuevo/', views.TallerCreateView.as_view(), name='crear'),
    path('<uuid:pk>/', views.TallerDetailView.as_view(), name='detalle'),
    path('<uuid:pk>/editar/', views.TallerUpdateView.as_view(), name='editar'),
    path('<uuid:pk>/sesion/', views.SesionCreateView.as_view(), name='sesion_crear'),
    path('sesion/<uuid:pk>/inscribir/', views.InscripcionCreateView.as_view(), name='inscribir'),
    path('sesion/<uuid:pk>/asistencia/', views.registrar_asistencia, name='asistencia'),
    path('inscripcion/<uuid:pk>/certificado/', views.generar_certificado, name='certificado'),
    path('inscripcion/<uuid:pk>/evaluar/', views.EvaluacionCreateView.as_view(), name='evaluar'),
]
