"""
Permisos personalizados para la API REST.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso para solo permitir escritura a administradores.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.rol == 'ADMIN'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso para solo permitir acceso al propietario o administrador.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.rol == 'ADMIN':
            return True

        # Verificar si el objeto tiene un campo de usuario
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        if hasattr(obj, 'usuario_principal'):
            return obj.usuario_principal == request.user

        return False


class EmpresaAnclaPermission(permissions.BasePermission):
    """
    Permiso para acceso a empresas ancla.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admins pueden todo
        if request.user.rol == 'ADMIN':
            return True

        # Lectura permitida para usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True

        # Solo admins y usuarios de empresa ancla pueden modificar
        return request.user.rol in ['ADMIN', 'EMPRESA_ANCLA']

    def has_object_permission(self, request, view, obj):
        if request.user.rol == 'ADMIN':
            return True

        # Verificar si el usuario pertenece a esta empresa
        return obj.usuarios_empresa.filter(usuario=request.user).exists()


class ProyectoPermission(permissions.BasePermission):
    """
    Permiso para acceso a proyectos.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.rol == 'ADMIN':
            return True

        # Consultor líder del proyecto
        if obj.consultor_lider == user:
            return True

        # Usuario de la empresa ancla
        if obj.empresa_ancla.usuarios_empresa.filter(usuario=user).exists():
            return True

        # Proveedor del proyecto
        if obj.proveedores_proyecto.filter(proveedor__usuario_principal=user).exists():
            return True

        return False


class ConsultorPermission(permissions.BasePermission):
    """
    Permiso para consultores.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ['ADMIN', 'CONSULTOR']


class ProveedorPermission(permissions.BasePermission):
    """
    Permiso para proveedores.
    Solo pueden ver/editar su propia información.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.rol == 'ADMIN':
            return True

        # Si es un proveedor, verificar que sea su información
        if hasattr(obj, 'proveedor'):
            return obj.proveedor.usuario_principal == user
        if hasattr(obj, 'usuario_principal'):
            return obj.usuario_principal == user

        return False
