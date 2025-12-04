from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML, Div

from apps.core.models import Usuario
from apps.proveedores.models import Proveedor
from .models import Proyecto, ProveedorProyecto, DocumentoProyecto


class ProyectoForm(forms.ModelForm):
    """Formulario para crear/editar proyectos."""

    class Meta:
        model = Proyecto
        fields = [
            'nombre', 'empresa_ancla', 'descripcion',
            'fecha_inicio', 'fecha_fin_planeada',
            'estado', 'director_proyecto',
            'numero_proveedores_planeado', 'duracion_meses', 'horas_por_proveedor',
            'presupuesto', 'costo_por_proveedor',
            'objetivos', 'alcance', 'notas'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_planeada': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'objetivos': forms.Textarea(attrs={'rows': 3}),
            'alcance': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar directores (solo consultores y admins)
        self.fields['director_proyecto'].queryset = Usuario.objects.filter(
            rol__in=['ADMIN', 'CONSULTOR'],
            is_active=True
        )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Información Básica',
                Row(
                    Column('nombre', css_class='col-md-6'),
                    Column('empresa_ancla', css_class='col-md-6'),
                ),
                'descripcion',
            ),
            Fieldset(
                'Fechas y Estado',
                Row(
                    Column('fecha_inicio', css_class='col-md-4'),
                    Column('fecha_fin_planeada', css_class='col-md-4'),
                    Column('estado', css_class='col-md-4'),
                ),
                'director_proyecto',
            ),
            Fieldset(
                'Configuración',
                Row(
                    Column('numero_proveedores_planeado', css_class='col-md-4'),
                    Column('duracion_meses', css_class='col-md-4'),
                    Column('horas_por_proveedor', css_class='col-md-4'),
                ),
                Row(
                    Column('presupuesto', css_class='col-md-6'),
                    Column('costo_por_proveedor', css_class='col-md-6'),
                ),
            ),
            Fieldset(
                'Detalles',
                'objetivos',
                'alcance',
                'notas',
            ),
            Div(
                Submit('submit', 'Guardar', css_class='btn btn-primary'),
                HTML('<a href="{% url \'proyectos:lista\' %}" class="btn btn-secondary ms-2">Cancelar</a>'),
                css_class='mt-4'
            )
        )


class ProveedorProyectoForm(forms.ModelForm):
    """Formulario para asignar proveedor a proyecto."""

    class Meta:
        model = ProveedorProyecto
        fields = [
            'proveedor', 'consultor_asignado',
            'fecha_inicio', 'fecha_fin_planeada', 'horas_planeadas',
            'notas'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_planeada': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto

        # Filtrar consultores
        self.fields['consultor_asignado'].queryset = Usuario.objects.filter(
            rol__in=['ADMIN', 'CONSULTOR'],
            is_active=True
        )

        # Filtrar proveedores que no están ya en el proyecto
        if proyecto:
            proveedores_en_proyecto = proyecto.proveedores.values_list('proveedor_id', flat=True)
            self.fields['proveedor'].queryset = Proveedor.objects.exclude(
                id__in=proveedores_en_proyecto
            )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'proveedor',
            'consultor_asignado',
            Row(
                Column('fecha_inicio', css_class='col-md-4'),
                Column('fecha_fin_planeada', css_class='col-md-4'),
                Column('horas_planeadas', css_class='col-md-4'),
            ),
            'notas',
            Submit('submit', 'Asignar Proveedor', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proyecto:
            instance.proyecto = self.proyecto
        if commit:
            instance.save()
        return instance


class AsignarMultiplesProveedoresForm(forms.Form):
    """Formulario para asignar múltiples proveedores a un proyecto."""

    proveedores = forms.ModelMultipleChoiceField(
        queryset=Proveedor.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Proveedores'
    )
    consultor_asignado = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol__in=['ADMIN', 'CONSULTOR'], is_active=True),
        required=False,
        label='Consultor asignado (opcional)'
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de inicio'
    )

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto

        if proyecto:
            # Excluir proveedores ya asignados
            proveedores_en_proyecto = proyecto.proveedores.values_list('proveedor_id', flat=True)
            self.fields['proveedores'].queryset = Proveedor.objects.exclude(
                id__in=proveedores_en_proyecto
            )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'proveedores',
            Row(
                Column('consultor_asignado', css_class='col-md-6'),
                Column('fecha_inicio', css_class='col-md-6'),
            ),
            Submit('submit', 'Asignar Proveedores', css_class='btn btn-primary')
        )


class CambiarConsultorForm(forms.Form):
    """Formulario para cambiar consultor asignado."""

    consultor_asignado = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol__in=['ADMIN', 'CONSULTOR'], is_active=True),
        label='Nuevo consultor'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'consultor_asignado',
            Submit('submit', 'Cambiar Consultor', css_class='btn btn-primary')
        )


class DocumentoProyectoForm(forms.ModelForm):
    """Formulario para subir documentos del proyecto."""

    class Meta:
        model = DocumentoProyecto
        fields = ['tipo', 'nombre', 'descripcion', 'archivo', 'version']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
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
            'descripcion',
            Row(
                Column('archivo', css_class='col-md-8'),
                Column('version', css_class='col-md-4'),
            ),
            Submit('submit', 'Subir Documento', css_class='btn btn-primary')
        )
