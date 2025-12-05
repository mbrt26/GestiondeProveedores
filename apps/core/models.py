import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""

    def create_user(self, email, password=None, **extra_fields):
        """Crear y guardar un usuario con email y contraseña."""
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crear y guardar un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('rol', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado usando email como identificador."""

    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        EMPRESA_ANCLA = 'EMPRESA_ANCLA', 'Empresa Ancla'
        PROVEEDOR = 'PROVEEDOR', 'Proveedor'
        CONSULTOR = 'CONSULTOR', 'Consultor'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('Correo electrónico', unique=True)
    nombre = models.CharField('Nombre', max_length=150)
    apellido = models.CharField('Apellido', max_length=150)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    rol = models.CharField(
        'Rol',
        max_length=20,
        choices=Rol.choices,
        default=Rol.CONSULTOR
    )
    avatar = models.ImageField(
        'Avatar',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    cargo = models.CharField('Cargo', max_length=100, blank=True)

    is_staff = models.BooleanField('Es staff', default=False)
    is_active = models.BooleanField('Activo', default=True)
    date_joined = models.DateTimeField('Fecha de registro', default=timezone.now)
    last_login = models.DateTimeField('Último acceso', blank=True, null=True)

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre

    def get_full_name(self):
        return self.nombre_completo

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def es_empresa_ancla(self):
        return self.rol == self.Rol.EMPRESA_ANCLA

    @property
    def es_proveedor(self):
        return self.rol == self.Rol.PROVEEDOR

    @property
    def es_consultor(self):
        return self.rol == self.Rol.CONSULTOR


class AuditoriaModel(models.Model):
    """Modelo abstracto para auditoría."""

    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='Creado por'
    )
    updated_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='Actualizado por'
    )

    class Meta:
        abstract = True


class ConfiguracionSistema(models.Model):
    """Configuración general del sistema."""

    clave = models.CharField('Clave', max_length=100, unique=True)
    valor = models.TextField('Valor')
    descripcion = models.TextField('Descripción', blank=True)
    tipo = models.CharField(
        'Tipo',
        max_length=20,
        choices=[
            ('STRING', 'Texto'),
            ('INTEGER', 'Número entero'),
            ('FLOAT', 'Número decimal'),
            ('BOOLEAN', 'Booleano'),
            ('JSON', 'JSON'),
        ],
        default='STRING'
    )
    is_active = models.BooleanField('Activo', default=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
        ordering = ['clave']

    def __str__(self):
        return self.clave

    @classmethod
    def get_valor(cls, clave, default=None):
        """Obtener valor de configuración por clave."""
        try:
            config = cls.objects.get(clave=clave, is_active=True)
            if config.tipo == 'INTEGER':
                return int(config.valor)
            elif config.tipo == 'FLOAT':
                return float(config.valor)
            elif config.tipo == 'BOOLEAN':
                return config.valor.lower() in ('true', '1', 'yes')
            elif config.tipo == 'JSON':
                import json
                return json.loads(config.valor)
            return config.valor
        except cls.DoesNotExist:
            return default


class LogActividad(models.Model):
    """Log de actividades del sistema."""

    class Accion(models.TextChoices):
        CREAR = 'CREAR', 'Crear'
        EDITAR = 'EDITAR', 'Editar'
        ELIMINAR = 'ELIMINAR', 'Eliminar'
        LOGIN = 'LOGIN', 'Inicio de sesión'
        LOGOUT = 'LOGOUT', 'Cierre de sesión'
        EXPORTAR = 'EXPORTAR', 'Exportar'
        IMPORTAR = 'IMPORTAR', 'Importar'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actividades'
    )
    accion = models.CharField('Acción', max_length=20, choices=Accion.choices)
    modelo = models.CharField('Modelo', max_length=100, blank=True)
    objeto_id = models.CharField('ID del objeto', max_length=100, blank=True)
    descripcion = models.TextField('Descripción')
    datos_anteriores = models.JSONField('Datos anteriores', null=True, blank=True)
    datos_nuevos = models.JSONField('Datos nuevos', null=True, blank=True)
    ip_address = models.GenericIPAddressField('Dirección IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    created_at = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.created_at}"
