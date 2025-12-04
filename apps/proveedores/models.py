import uuid
from django.db import models
from apps.core.models import AuditoriaModel, Usuario
from apps.empresas.models import EmpresaAncla


class Proveedor(AuditoriaModel):
    """Modelo para proveedores (empresas beneficiarias del programa)."""

    class TamanoEmpresa(models.TextChoices):
        MICRO = 'MICRO', 'Microempresa (1-10 empleados)'
        PEQUENA = 'PEQUENA', 'Pequeña empresa (11-50 empleados)'
        MEDIANA = 'MEDIANA', 'Mediana empresa (51-200 empleados)'
        GRANDE = 'GRANDE', 'Gran empresa (más de 200 empleados)'

    class SectorEconomico(models.TextChoices):
        MANUFACTURA = 'MANUFACTURA', 'Manufactura'
        CONSTRUCCION = 'CONSTRUCCION', 'Construcción'
        COMERCIO = 'COMERCIO', 'Comercio'
        SERVICIOS = 'SERVICIOS', 'Servicios'
        TECNOLOGIA = 'TECNOLOGIA', 'Tecnología'
        AGROINDUSTRIA = 'AGROINDUSTRIA', 'Agroindustria'
        TRANSPORTE = 'TRANSPORTE', 'Transporte y Logística'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica
    razon_social = models.CharField('Razón social', max_length=250)
    nit = models.CharField('NIT', max_length=20, unique=True)
    nombre_comercial = models.CharField('Nombre comercial', max_length=200, blank=True)

    # Representante legal
    representante_legal = models.CharField('Representante legal', max_length=200)
    cedula_representante = models.CharField('Cédula del representante', max_length=20, blank=True)

    # Contacto
    email = models.EmailField('Email')
    telefono = models.CharField('Teléfono', max_length=20)
    celular = models.CharField('Celular', max_length=20, blank=True)
    direccion = models.TextField('Dirección')
    ciudad = models.CharField('Ciudad', max_length=100)
    departamento = models.CharField('Departamento', max_length=100)
    codigo_postal = models.CharField('Código postal', max_length=10, blank=True)

    # Información empresarial
    sector_economico = models.CharField(
        'Sector económico',
        max_length=20,
        choices=SectorEconomico.choices,
        default=SectorEconomico.OTRO
    )
    actividad_economica = models.CharField('Actividad económica', max_length=200, blank=True)
    codigo_ciiu = models.CharField('Código CIIU', max_length=10, blank=True)
    tamano_empresa = models.CharField(
        'Tamaño de empresa',
        max_length=10,
        choices=TamanoEmpresa.choices,
        default=TamanoEmpresa.MICRO
    )
    numero_empleados = models.PositiveIntegerField('Número de empleados', default=1)
    anio_constitucion = models.PositiveIntegerField('Año de constitución', null=True, blank=True)
    sitio_web = models.URLField('Sitio web', blank=True)

    # Información financiera (opcional)
    ventas_anuales = models.DecimalField(
        'Ventas anuales (COP)',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    activos_totales = models.DecimalField(
        'Activos totales (COP)',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Contacto adicional
    contacto_nombre = models.CharField('Nombre del contacto', max_length=200, blank=True)
    contacto_cargo = models.CharField('Cargo del contacto', max_length=100, blank=True)
    contacto_email = models.EmailField('Email del contacto', blank=True)
    contacto_telefono = models.CharField('Teléfono del contacto', max_length=20, blank=True)

    # Archivos
    logo = models.ImageField('Logo', upload_to='proveedores/logos/', blank=True, null=True)
    rut = models.FileField('RUT', upload_to='proveedores/documentos/', blank=True, null=True)
    camara_comercio = models.FileField(
        'Cámara de Comercio',
        upload_to='proveedores/documentos/',
        blank=True,
        null=True
    )

    # Descripción
    descripcion = models.TextField('Descripción de la empresa', blank=True)
    productos_servicios = models.TextField('Productos/Servicios que ofrece', blank=True)

    # Usuario asociado (para acceso al portal)
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proveedor',
        verbose_name='Usuario de acceso'
    )

    # Notas internas
    notas = models.TextField('Notas internas', blank=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']

    def __str__(self):
        return self.nombre_comercial or self.razon_social

    @property
    def nombre_display(self):
        return self.nombre_comercial or self.razon_social

    @property
    def proyectos_activos(self):
        """Número de proyectos activos en los que participa."""
        return self.participaciones.filter(
            estado='EN_PROCESO',
            proyecto__estado='EN_CURSO'
        ).count()


class ProveedorEmpresaAncla(models.Model):
    """Relación entre proveedores y empresas ancla."""

    class EstadoVinculacion(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='empresas_vinculadas',
        verbose_name='Proveedor'
    )
    empresa_ancla = models.ForeignKey(
        EmpresaAncla,
        on_delete=models.CASCADE,
        related_name='proveedores_vinculados',
        verbose_name='Empresa Ancla'
    )
    fecha_vinculacion = models.DateField('Fecha de vinculación', auto_now_add=True)
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=EstadoVinculacion.choices,
        default=EstadoVinculacion.ACTIVO
    )
    categoria = models.CharField('Categoría', max_length=100, blank=True)
    codigo_proveedor = models.CharField(
        'Código de proveedor',
        max_length=50,
        blank=True,
        help_text='Código interno del proveedor en la empresa ancla'
    )
    notas = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Vinculación Proveedor-Empresa'
        verbose_name_plural = 'Vinculaciones Proveedor-Empresa'
        unique_together = ['proveedor', 'empresa_ancla']
        ordering = ['empresa_ancla', 'proveedor']

    def __str__(self):
        return f"{self.proveedor} - {self.empresa_ancla}"


class DocumentoProveedor(models.Model):
    """Documentos adicionales del proveedor."""

    class TipoDocumento(models.TextChoices):
        RUT = 'RUT', 'RUT'
        CAMARA_COMERCIO = 'CAMARA_COMERCIO', 'Cámara de Comercio'
        ESTADOS_FINANCIEROS = 'ESTADOS_FINANCIEROS', 'Estados Financieros'
        CERTIFICACION = 'CERTIFICACION', 'Certificación'
        POLIZA = 'POLIZA', 'Póliza de Seguros'
        OTRO = 'OTRO', 'Otro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Proveedor'
    )
    tipo = models.CharField(
        'Tipo de documento',
        max_length=20,
        choices=TipoDocumento.choices
    )
    nombre = models.CharField('Nombre del documento', max_length=200)
    archivo = models.FileField('Archivo', upload_to='proveedores/documentos/')
    fecha_emision = models.DateField('Fecha de emisión', null=True, blank=True)
    fecha_vencimiento = models.DateField('Fecha de vencimiento', null=True, blank=True)
    notas = models.TextField('Notas', blank=True)
    uploaded_at = models.DateTimeField('Subido', auto_now_add=True)
    uploaded_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Subido por'
    )

    class Meta:
        verbose_name = 'Documento del Proveedor'
        verbose_name_plural = 'Documentos del Proveedor'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.proveedor} - {self.nombre}"

    @property
    def esta_vencido(self):
        if self.fecha_vencimiento:
            from django.utils import timezone
            return self.fecha_vencimiento < timezone.now().date()
        return False
