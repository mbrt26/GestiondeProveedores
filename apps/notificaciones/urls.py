from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('', views.NotificacionListView.as_view(), name='lista'),
    path('no-leidas/', views.NotificacionesNoLeidasView.as_view(), name='no_leidas'),
    path('marcar-leida/<uuid:pk>/', views.MarcarLeidaView.as_view(), name='marcar_leida'),
    path('marcar-todas-leidas/', views.MarcarTodasLeidasView.as_view(), name='marcar_todas_leidas'),
    path('configuracion/', views.ConfiguracionNotificacionView.as_view(), name='configuracion'),
]
