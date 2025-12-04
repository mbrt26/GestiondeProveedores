from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea administrador."""

    def test_func(self):
        return self.request.user.es_admin

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("No tiene permisos para acceder a esta sección.")
        return super().handle_no_permission()


class ConsultorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea consultor o admin."""

    def test_func(self):
        return self.request.user.es_admin or self.request.user.es_consultor


class EmpresaAnclaRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea de empresa ancla, consultor o admin."""

    def test_func(self):
        user = self.request.user
        return user.es_admin or user.es_consultor or user.es_empresa_ancla


class ProveedorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea proveedor."""

    def test_func(self):
        return self.request.user.es_proveedor


class MultiRoleMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que acepta múltiples roles."""
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        if user.es_admin:
            return True
        return user.rol in self.allowed_roles


class AuditMixin:
    """Mixin para agregar auditoría a las vistas."""

    def form_valid(self, form):
        if hasattr(form.instance, 'created_by') and not form.instance.pk:
            form.instance.created_by = self.request.user
        if hasattr(form.instance, 'updated_by'):
            form.instance.updated_by = self.request.user
        return super().form_valid(form)


class EmpresaAnclaMixin:
    """Mixin para filtrar objetos por empresa ancla del usuario."""

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.es_admin:
            return queryset

        if user.es_empresa_ancla:
            empresas_ids = user.empresas_ancla.values_list('empresa_ancla_id', flat=True)
            return queryset.filter(empresa_ancla_id__in=empresas_ids)

        if user.es_consultor:
            # Consultores ven los proyectos asignados
            from apps.proyectos.models import ProveedorProyecto
            proyectos_ids = ProveedorProyecto.objects.filter(
                consultor_asignado=user
            ).values_list('proyecto_id', flat=True)
            if hasattr(queryset.model, 'proyecto'):
                return queryset.filter(proyecto_id__in=proyectos_ids)
            return queryset

        return queryset.none()
