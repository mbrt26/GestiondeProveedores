from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML, Div

from .models import EmpresaAncla, UsuarioEmpresaAncla


class EmpresaAnclaForm(forms.ModelForm):
    """Formulario para crear/editar empresas ancla."""

    class Meta:
        model = EmpresaAncla
        fields = [
            'nombre', 'nit', 'razon_social', 'logo',
            'direccion', 'ciudad', 'departamento', 'pais',
            'telefono', 'email', 'sitio_web',
            'sector_economico', 'descripcion', 'numero_empleados', 'anio_fundacion',
            'contacto_nombre', 'contacto_cargo', 'contacto_email', 'contacto_telefono',
            'notas', 'is_active'
        ]
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 3}),
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
                    Column('nombre', css_class='col-md-6'),
                    Column('nit', css_class='col-md-3'),
                    Column('sector_economico', css_class='col-md-3'),
                ),
                Row(
                    Column('razon_social', css_class='col-md-8'),
                    Column('logo', css_class='col-md-4'),
                ),
            ),
            Fieldset(
                'Ubicación y Contacto',
                'direccion',
                Row(
                    Column('ciudad', css_class='col-md-4'),
                    Column('departamento', css_class='col-md-4'),
                    Column('pais', css_class='col-md-4'),
                ),
                Row(
                    Column('telefono', css_class='col-md-4'),
                    Column('email', css_class='col-md-4'),
                    Column('sitio_web', css_class='col-md-4'),
                ),
            ),
            Fieldset(
                'Información Adicional',
                'descripcion',
                Row(
                    Column('numero_empleados', css_class='col-md-6'),
                    Column('anio_fundacion', css_class='col-md-6'),
                ),
            ),
            Fieldset(
                'Contacto Principal',
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
                'Configuración',
                'notas',
                'is_active',
            ),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url \'empresas:lista\' %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-4'
            )
        )


class UsuarioEmpresaAnclaForm(forms.ModelForm):
    """Formulario para asignar usuarios a empresas ancla."""

    class Meta:
        model = UsuarioEmpresaAncla
        fields = ['usuario', 'rol', 'is_active']

    def __init__(self, *args, empresa_ancla=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa_ancla = empresa_ancla
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'usuario',
            'rol',
            'is_active',
            Submit('submit', 'Asignar', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.empresa_ancla:
            instance.empresa_ancla = self.empresa_ancla
        if commit:
            instance.save()
        return instance
