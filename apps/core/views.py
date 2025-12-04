from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
)

from .forms import (
    LoginForm, UsuarioCreationForm, UsuarioUpdateForm, PerfilForm,
    CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm
)
from .models import Usuario, LogActividad
from .mixins import AdminRequiredMixin


class CustomLoginView(LoginView):
    """Vista de inicio de sesión."""
    template_name = 'auth/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:dashboard')


class CustomLogoutView(LogoutView):
    """Vista de cierre de sesión."""
    next_page = 'core:login'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal del sistema."""
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Importar modelos aquí para evitar imports circulares
        from apps.empresas.models import EmpresaAncla
        from apps.proveedores.models import Proveedor
        from apps.proyectos.models import Proyecto, ProveedorProyecto

        # Estadísticas generales según el rol
        if user.es_admin or user.es_consultor:
            context['total_empresas'] = EmpresaAncla.objects.filter(is_active=True).count()
            context['total_proveedores'] = Proveedor.objects.count()
            context['total_proyectos'] = Proyecto.objects.exclude(estado='CANCELADO').count()
            context['proyectos_activos'] = Proyecto.objects.filter(estado='EN_CURSO').count()

            # Proveedores por etapa
            context['proveedores_etapa_1'] = ProveedorProyecto.objects.filter(
                etapa_actual=1, estado='EN_PROCESO'
            ).count()
            context['proveedores_etapa_2'] = ProveedorProyecto.objects.filter(
                etapa_actual=2, estado='EN_PROCESO'
            ).count()
            context['proveedores_etapa_3'] = ProveedorProyecto.objects.filter(
                etapa_actual=3, estado='EN_PROCESO'
            ).count()
            context['proveedores_etapa_4'] = ProveedorProyecto.objects.filter(
                etapa_actual=4, estado='EN_PROCESO'
            ).count()

            # Proyectos recientes
            context['proyectos_recientes'] = Proyecto.objects.filter(
                estado='EN_CURSO'
            ).order_by('-created_at')[:5]

            # Actividad reciente
            context['actividad_reciente'] = LogActividad.objects.select_related(
                'usuario'
            ).order_by('-created_at')[:10]

        elif user.es_empresa_ancla:
            # Filtrar por empresas asociadas al usuario
            empresas_ids = user.empresas_ancla.values_list('empresa_ancla_id', flat=True)
            context['mis_proyectos'] = Proyecto.objects.filter(
                empresa_ancla_id__in=empresas_ids
            ).order_by('-created_at')[:10]
            context['total_mis_proveedores'] = ProveedorProyecto.objects.filter(
                proyecto__empresa_ancla_id__in=empresas_ids
            ).values('proveedor').distinct().count()

        elif user.es_proveedor:
            # Proyectos del proveedor
            try:
                proveedor = user.proveedor
                context['mis_participaciones'] = ProveedorProyecto.objects.filter(
                    proveedor=proveedor
                ).select_related('proyecto').order_by('-fecha_inicio')
            except:
                context['mis_participaciones'] = []

        return context


class PerfilView(LoginRequiredMixin, UpdateView):
    """Vista para editar el perfil del usuario."""
    model = Usuario
    form_class = PerfilForm
    template_name = 'core/perfil.html'
    success_url = reverse_lazy('core:perfil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)


class CambiarPasswordView(LoginRequiredMixin, PasswordChangeView):
    """Vista para cambiar contraseña."""
    form_class = CustomPasswordChangeForm
    template_name = 'core/cambiar_password.html'
    success_url = reverse_lazy('core:perfil')

    def form_valid(self, form):
        messages.success(self.request, 'Contraseña cambiada correctamente.')
        return super().form_valid(form)


# Gestión de Usuarios (Solo Admin)
class UsuarioListView(AdminRequiredMixin, ListView):
    """Lista de usuarios del sistema."""
    model = Usuario
    template_name = 'core/usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        queryset = Usuario.objects.all().order_by('nombre', 'apellido')

        # Filtros
        rol = self.request.GET.get('rol')
        estado = self.request.GET.get('estado')
        buscar = self.request.GET.get('buscar')

        if rol:
            queryset = queryset.filter(rol=rol)
        if estado:
            queryset = queryset.filter(is_active=(estado == 'activo'))
        if buscar:
            queryset = queryset.filter(
                Q(nombre__icontains=buscar) |
                Q(apellido__icontains=buscar) |
                Q(email__icontains=buscar)
            )

        return queryset


class UsuarioCreateView(AdminRequiredMixin, CreateView):
    """Crear nuevo usuario."""
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'core/usuarios/form.html'
    success_url = reverse_lazy('core:usuarios_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)


class UsuarioUpdateView(AdminRequiredMixin, UpdateView):
    """Editar usuario existente."""
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'core/usuarios/form.html'
    success_url = reverse_lazy('core:usuarios_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado correctamente.')
        return super().form_valid(form)


class UsuarioDetailView(AdminRequiredMixin, DetailView):
    """Detalle de usuario."""
    model = Usuario
    template_name = 'core/usuarios/detalle.html'
    context_object_name = 'usuario'


@login_required
def toggle_usuario_activo(request, pk):
    """Activar/Desactivar usuario via AJAX."""
    if not request.user.es_admin:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        return JsonResponse({'error': 'No puede desactivarse a sí mismo'}, status=400)

    usuario.is_active = not usuario.is_active
    usuario.save()

    return JsonResponse({
        'success': True,
        'is_active': usuario.is_active,
        'message': f'Usuario {"activado" if usuario.is_active else "desactivado"} correctamente.'
    })


# Vistas de error
def error_404(request, exception):
    """Página de error 404."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Página de error 500."""
    return render(request, 'errors/500.html', status=500)
