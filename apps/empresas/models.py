import uuid
from django.db import models
from apps.core.models import AuditoriaModel, Usuario


class EmpresaAncla(AuditoriaModel):
    """Modelo para empresas ancla (clientes principales)."""

    class SectorEconomico(models.TextChoices):
        MANUFACTURA = 'MANUFACTURA', 'Manufactura'
        CONSTRUCCION = 'CONSTRUCCION', 'Construcción'
        COMERCIO = 'COMERCIO', 'Comercio'
        SERVICIOS = 'SERVICIOS', 'Servicios'
        TECNOLOGIA = 'TECNOLOGIA', 'Tecnología'
        AGROINDUSTRIA = 'AGROINDUSTRIA', 'Agroindustria'
        ENERGIA = 'ENERGIA', 'Energía y Minería'
        FINANCIERO = 'FINANCIERO', 'Sector Financiero'
        SALUD = 'SALUD', 'Salud'
        EDUCACION = 'EDUCACION', 'Educación'
        TRANSPORTE = 'TRANSPORTE', 'Transporte y Logística'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField('Nombre de la empresa', max_length=200)
    nit = models.CharField('NIT', max_length=20, unique=True)
    razon_social = models.CharField('Razón social', max_length=250, blank=True)

    # Información de contacto
    direccion = models.TextField('Dirección', blank=True)
    ciudad = models.CharField('Ciudad', max_length=100, blank=True)
    departamento = models.CharField('Departamento', max_length=100, blank=True)
    pais = models.CharField('País', max_length=100, default='Colombia')
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Email corporativo', blank=True)
    sitio_web = models.URLField('Sitio web', blank=True)

    # Información empresarial
    sector_economico = models.CharField(
        'Sector económico',
        max_length=20,
        choices=SectorEconomico.choices,
        default=SectorEconomico.OTRO
    )
    descripcion = models.TextField('Descripción', blank=True)
    numero_empleados = models.PositiveIntegerField('Número de empleados', null=True, blank=True)
    anio_fundacion = models.PositiveIntegerField('Año de fundación', null=True, blank=True)

    # Contacto principal
    contacto_nombre = models.CharField('Nombre del contacto', max_length=200, blank=True)
    contacto_cargo = models.CharField('Cargo del contacto', max_length=100, blank=True)
    contacto_email = models.EmailField('Email del contacto', blank=True)
    contacto_telefono = models.CharField('Teléfono del contacto', max_length=20, blank=True)

    # Archivos
    logo = models.ImageField('Logo', upload_to='empresas/logos/', blank=True, null=True)

    # Configuración
    configuracion = models.JSONField('Configuración', default=dict, blank=True)
    notas = models.TextField('Notas internas', blank=True)

    # Estado
    is_active = models.BooleanField('Activa', default=True)

    class Meta:
        verbose_name = 'Empresa Ancla'
        verbose_name_plural = 'Empresas Ancla'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def proyectos_activos(self):
        """Retorna el número de proyectos activos."""
        return self.proyectos.filter(estado='EN_CURSO').count()

    @property
    def total_proveedores(self):
        """Retorna el número total de proveedores vinculados."""
        return self.proveedores_vinculados.filter(estado='ACTIVO').count()


class UsuarioEmpresaAncla(models.Model):
    """Relación entre usuarios y empresas ancla."""

    class RolEmpresa(models.TextChoices):
        ADMIN_EMPRESA = 'ADMIN_EMPRESA', 'Administrador'
        GESTOR = 'GESTOR', 'Gestor'
        VISUALIZADOR = 'VISUALIZADOR', 'Visualizador'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='empresas_ancla',
        verbose_name='Usuario'
    )
    empresa_ancla = models.ForeignKey(
        EmpresaAncla,
        on_delete=models.CASCADE,
        related_name='usuarios',
        verbose_name='Empresa Ancla'
    )
    rol = models.CharField(
        'Rol en la empresa',
        max_length=20,
        choices=RolEmpresa.choices,
        default=RolEmpresa.VISUALIZADOR
    )
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario de Empresa Ancla'
        verbose_name_plural = 'Usuarios de Empresas Ancla'
        unique_together = ['usuario', 'empresa_ancla']
        ordering = ['empresa_ancla', 'usuario']

    def __str__(self):
        return f"{self.usuario} - {self.empresa_ancla}"
