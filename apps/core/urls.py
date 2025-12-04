from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación
    path('', views.CustomLoginView.as_view(), name='login'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Perfil
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
    path('perfil/cambiar-password/', views.CambiarPasswordView.as_view(), name='cambiar_password'),

    # Reset de contraseña
    path('password-reset/',
         PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
         name='password_reset_complete'),

    # Gestión de usuarios (Admin)
    path('usuarios/', views.UsuarioListView.as_view(), name='usuarios_lista'),
    path('usuarios/nuevo/', views.UsuarioCreateView.as_view(), name='usuarios_crear'),
    path('usuarios/<uuid:pk>/', views.UsuarioDetailView.as_view(), name='usuarios_detalle'),
    path('usuarios/<uuid:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuarios_editar'),
    path('usuarios/<uuid:pk>/toggle/', views.toggle_usuario_activo, name='usuarios_toggle'),
]
