from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset

from .models import (
    VozCliente, DiagnosticoCompetitividad, ObjetivoFortalecimiento, DocumentoEtapa1,
    HallazgoProblema, AccionMejora, CronogramaImplementacion,
    TareaImplementacion, EvidenciaImplementacion, SesionAcompanamiento,
    IndicadorKPI, MedicionKPI, ReporteSemanal, EvaluacionDirectiva, InformeCierre
)


# ============================================================================
# ETAPA 1 FORMS
# ============================================================================

class VozClienteForm(forms.ModelForm):
    class Meta:
        model = VozCliente
        fields = [
            'empresa_ancla_contacto', 'cargo_contacto', 'fecha_entrevista',
            'necesidades_identificadas', 'expectativas', 'requerimientos_especificos',
            'fortalezas_proveedor', 'areas_mejora', 'archivo_evidencia'
        ]
        widgets = {
            'fecha_entrevista': forms.DateInput(attrs={'type': 'date'}),
            'necesidades_identificadas': forms.Textarea(attrs={'rows': 3}),
            'expectativas': forms.Textarea(attrs={'rows': 3}),
            'requerimientos_especificos': forms.Textarea(attrs={'rows': 3}),
            'fortalezas_proveedor': forms.Textarea(attrs={'rows': 3}),
            'areas_mejora': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = DiagnosticoCompetitividad
        fields = [
            'area_evaluada', 'nivel_madurez', 'puntaje',
            'fortalezas', 'debilidades', 'oportunidades', 'amenazas', 'observaciones'
        ]
        widgets = {
            'fortalezas': forms.Textarea(attrs={'rows': 3}),
            'debilidades': forms.Textarea(attrs={'rows': 3}),
            'oportunidades': forms.Textarea(attrs={'rows': 3}),
            'amenazas': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class ObjetivoForm(forms.ModelForm):
    class Meta:
        model = ObjetivoFortalecimiento
        fields = [
            'objetivo', 'especifico', 'medible', 'alcanzable', 'relevante', 'temporal',
            'valor_inicial', 'valor_meta', 'unidad_medida', 'prioridad'
        ]
        widgets = {
            'objetivo': forms.Textarea(attrs={'rows': 2}),
            'especifico': forms.Textarea(attrs={'rows': 2}),
            'alcanzable': forms.Textarea(attrs={'rows': 2}),
            'relevante': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class DocumentoEtapa1Form(forms.ModelForm):
    class Meta:
        model = DocumentoEtapa1
        fields = ['tipo', 'nombre', 'archivo', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Subir', css_class='btn btn-primary'))


# ============================================================================
# ETAPA 2 FORMS
# ============================================================================

class HallazgoForm(forms.ModelForm):
    class Meta:
        model = HallazgoProblema
        fields = ['hallazgo', 'problema_identificado', 'causa_raiz', 'area_impactada', 'prioridad']
        widgets = {
            'hallazgo': forms.Textarea(attrs={'rows': 3}),
            'problema_identificado': forms.Textarea(attrs={'rows': 3}),
            'causa_raiz': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class AccionMejoraForm(forms.ModelForm):
    class Meta:
        model = AccionMejora
        fields = [
            'descripcion', 'tipo_accion', 'recursos_necesarios',
            'responsable_sugerido', 'impacto_esperado', 'esfuerzo_requerido', 'seleccionada'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'recursos_necesarios': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class CronogramaForm(forms.ModelForm):
    class Meta:
        model = CronogramaImplementacion
        fields = [
            'accion_mejora', 'actividad', 'fecha_inicio_planeada', 'fecha_fin_planeada',
            'responsable', 'recursos', 'entregable'
        ]
        widgets = {
            'fecha_inicio_planeada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_planeada': forms.DateInput(attrs={'type': 'date'}),
            'recursos': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, etapa2=None, **kwargs):
        super().__init__(*args, **kwargs)
        if etapa2:
            self.fields['accion_mejora'].queryset = AccionMejora.objects.filter(
                hallazgo__etapa2=etapa2,
                seleccionada=True
            )
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Agregar', css_class='btn btn-primary'))


# ============================================================================
# ETAPA 3 FORMS
# ============================================================================

class TareaForm(forms.ModelForm):
    class Meta:
        model = TareaImplementacion
        fields = [
            'titulo', 'descripcion', 'estado', 'prioridad',
            'fecha_inicio_planeada', 'fecha_fin_planeada',
            'responsable', 'porcentaje_avance', 'notas'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio_planeada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_planeada': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = EvidenciaImplementacion
        fields = ['tipo', 'nombre', 'archivo', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Subir', css_class='btn btn-primary'))


class SesionForm(forms.ModelForm):
    class Meta:
        model = SesionAcompanamiento
        fields = [
            'fecha', 'duracion_horas', 'modalidad',
            'temas_tratados', 'compromisos', 'participantes', 'archivo_acta'
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'temas_tratados': forms.Textarea(attrs={'rows': 3}),
            'compromisos': forms.Textarea(attrs={'rows': 3}),
            'participantes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Registrar', css_class='btn btn-primary'))


# ============================================================================
# ETAPA 4 FORMS
# ============================================================================

class IndicadorForm(forms.ModelForm):
    class Meta:
        model = IndicadorKPI
        fields = [
            'objetivo', 'nombre', 'descripcion',
            'valor_inicial', 'valor_meta', 'unidad_medida', 'frecuencia_medicion'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, etapa1=None, **kwargs):
        super().__init__(*args, **kwargs)
        if etapa1:
            self.fields['objetivo'].queryset = ObjetivoFortalecimiento.objects.filter(etapa1=etapa1)
        self.fields['objetivo'].required = False
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Crear', css_class='btn btn-primary'))


class MedicionForm(forms.ModelForm):
    class Meta:
        model = MedicionKPI
        fields = ['fecha_medicion', 'valor', 'observaciones']
        widgets = {
            'fecha_medicion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Registrar', css_class='btn btn-primary'))


class ReporteForm(forms.ModelForm):
    class Meta:
        model = ReporteSemanal
        fields = [
            'semana_numero', 'fecha_inicio_semana', 'fecha_fin_semana',
            'resumen_avance', 'logros', 'dificultades', 'proximas_acciones'
        ]
        widgets = {
            'fecha_inicio_semana': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_semana': forms.DateInput(attrs={'type': 'date'}),
            'resumen_avance': forms.Textarea(attrs={'rows': 3}),
            'logros': forms.Textarea(attrs={'rows': 3}),
            'dificultades': forms.Textarea(attrs={'rows': 3}),
            'proximas_acciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Crear', css_class='btn btn-primary'))


class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = EvaluacionDirectiva
        fields = [
            'fecha', 'participantes', 'objetivos_cumplidos',
            'objetivos_pendientes', 'ajustes_requeridos', 'decisiones_tomadas',
            'archivo_acta', 'aprobado'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'participantes': forms.Textarea(attrs={'rows': 2}),
            'objetivos_cumplidos': forms.Textarea(attrs={'rows': 3}),
            'objetivos_pendientes': forms.Textarea(attrs={'rows': 3}),
            'ajustes_requeridos': forms.Textarea(attrs={'rows': 3}),
            'decisiones_tomadas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Registrar', css_class='btn btn-primary'))


class InformeCierreForm(forms.ModelForm):
    class Meta:
        model = InformeCierre
        fields = [
            'resumen_ejecutivo', 'objetivos_logrados', 'mejoras_implementadas',
            'lecciones_aprendidas', 'recomendaciones'
        ]
        widgets = {
            'resumen_ejecutivo': forms.Textarea(attrs={'rows': 4}),
            'objetivos_logrados': forms.Textarea(attrs={'rows': 4}),
            'mejoras_implementadas': forms.Textarea(attrs={'rows': 4}),
            'lecciones_aprendidas': forms.Textarea(attrs={'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Generar Informe', css_class='btn btn-primary'))
