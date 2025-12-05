from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML, Div

from .models import Proveedor, ProveedorEmpresaAncla, DocumentoProveedor


class ProveedorForm(forms.ModelForm):
    """Formulario para crear/editar proveedores."""

    class Meta:
        model = Proveedor
        fields = [
            'razon_social', 'nit', 'nombre_comercial', 'logo',
            'representante_legal', 'cedula_representante',
            'email', 'telefono', 'celular',
            'direccion', 'ciudad', 'departamento', 'codigo_postal',
            'sector_economico', 'actividad_economica', 'codigo_ciiu',
            'tamano_empresa', 'numero_empleados', 'anio_constitucion', 'sitio_web',
            'ventas_anuales', 'activos_totales',
            'contacto_nombre', 'contacto_cargo', 'contacto_email', 'contacto_telefono',
            'descripcion', 'productos_servicios',
            'rut', 'camara_comercio', 'notas'
        ]
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'productos_servicios': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Información Básica',
                Row(
                    Column('razon_social', css_class='col-md-6'),
                    Column('nit', css_class='col-md-3'),
                    Column('nombre_comercial', css_class='col-md-3'),
                ),
                Row(
                    Column('representante_legal', css_class='col-md-6'),
                    Column('cedula_representante', css_class='col-md-3'),
                    Column('logo', css_class='col-md-3'),
                ),
            ),
            Fieldset(
                'Contacto',
                Row(
                    Column('email', css_class='col-md-4'),
                    Column('telefono', css_class='col-md-4'),
                    Column('celular', css_class='col-md-4'),
                ),
                'direccion',
                Row(
                    Column('ciudad', css_class='col-md-4'),
                    Column('departamento', css_class='col-md-4'),
                    Column('codigo_postal', css_class='col-md-4'),
                ),
            ),
            Fieldset(
                'Información Empresarial',
                Row(
                    Column('sector_economico', css_class='col-md-4'),
                    Column('tamano_empresa', css_class='col-md-4'),
                    Column('numero_empleados', css_class='col-md-4'),
                ),
                Row(
                    Column('actividad_economica', css_class='col-md-4'),
                    Column('codigo_ciiu', css_class='col-md-4'),
                    Column('anio_constitucion', css_class='col-md-4'),
                ),
                Row(
                    Column('sitio_web', css_class='col-md-4'),
                    Column('ventas_anuales', css_class='col-md-4'),
                    Column('activos_totales', css_class='col-md-4'),
                ),
            ),
            Fieldset(
                'Contacto Adicional',
                Row(
                    Column('contacto_nombre', css_class='col-md-6'),
                    Column('contacto_cargo', css_class='col-md-6'),
                ),
                Row(
                    Column('contacto_email', css_class='col-md-6'),
                    Column('contacto_telefono', css_class='col-md-6'),
                ),
            ),
            Fieldset(
                'Descripción',
                'descripcion',
                'productos_servicios',
            ),
            Fieldset(
                'Documentos',
                Row(
                    Column('rut', css_class='col-md-6'),
                    Column('camara_comercio', css_class='col-md-6'),
                ),
            ),
            Fieldset(
                'Notas',
                'notas',
            ),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url \'proveedores:lista\' %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-4'
            )
        )


class ProveedorEmpresaAnclaForm(forms.ModelForm):
    """Formulario para vincular proveedor a empresa ancla."""

    class Meta:
        model = ProveedorEmpresaAncla
        fields = ['empresa_ancla', 'estado', 'categoria', 'codigo_proveedor', 'notas']
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, proveedor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proveedor = proveedor
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'empresa_ancla',
            Row(
                Column('estado', css_class='col-md-6'),
                Column('categoria', css_class='col-md-6'),
            ),
            'codigo_proveedor',
            'notas',
            Submit('submit', 'Vincular', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proveedor:
            instance.proveedor = self.proveedor
        if commit:
            instance.save()
        return instance


class DocumentoProveedorForm(forms.ModelForm):
    """Formulario para subir documentos del proveedor."""

    class Meta:
        model = DocumentoProveedor
        fields = ['tipo', 'nombre', 'archivo', 'fecha_emision', 'fecha_vencimiento', 'notas']
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('tipo', css_class='col-md-6'),
                Column('nombre', css_class='col-md-6'),
            ),
            'archivo',
            Row(
                Column('fecha_emision', css_class='col-md-6'),
                Column('fecha_vencimiento', css_class='col-md-6'),
            ),
            'notas',
            Submit('submit', 'Subir Documento', css_class='btn btn-primary')
        )


class ImportarProveedoresForm(forms.Form):
    """Formulario para importar proveedores desde Excel."""

    archivo = forms.FileField(
        label='Archivo Excel',
        help_text='Seleccione un archivo Excel (.xlsx) con los datos de los proveedores'
    )
    empresa_ancla = forms.ModelChoiceField(
        queryset=None,
        label='Empresa Ancla',
        required=False,
        help_text='Seleccione la empresa ancla para vincular automáticamente los proveedores'
    )

    def __init__(self, *args, **kwargs):
        from apps.empresas.models import EmpresaAncla
        super().__init__(*args, **kwargs)
        self.fields['empresa_ancla'].queryset = EmpresaAncla.objects.filter(is_active=True)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'archivo',
            'empresa_ancla',
            Submit('submit', 'Importar', css_class='btn btn-primary')
        )
