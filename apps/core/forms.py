from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML, Field

from .models import Usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión personalizado."""

    username = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    remember_me = forms.BooleanField(
        label='Recordarme',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'username',
            'password',
            Div(
                Field('remember_me', wrapper_class='form-check'),
                css_class='mb-3'
            ),
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary w-100')
        )


class UsuarioCreationForm(UserCreationForm):
    """Formulario para crear usuarios."""

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido', 'telefono', 'rol', 'cargo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='col-md-6'),
                Column('apellido', css_class='col-md-6'),
            ),
            'email',
            Row(
                Column('telefono', css_class='col-md-6'),
                Column('cargo', css_class='col-md-6'),
            ),
            'rol',
            Row(
                Column('password1', css_class='col-md-6'),
                Column('password2', css_class='col-md-6'),
            ),
            Submit('submit', 'Crear Usuario', css_class='btn btn-primary')
        )


class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para editar usuarios."""

    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'telefono', 'cargo', 'avatar', 'rol', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='col-md-6'),
                Column('apellido', css_class='col-md-6'),
            ),
            Row(
                Column('telefono', css_class='col-md-6'),
                Column('cargo', css_class='col-md-6'),
            ),
            'avatar',
            Row(
                Column('rol', css_class='col-md-6'),
                Column('is_active', css_class='col-md-6'),
            ),
            Submit('submit', 'Actualizar', css_class='btn btn-primary')
        )


class PerfilForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario actual."""

    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'telefono', 'cargo', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('nombre', css_class='col-md-6'),
                Column('apellido', css_class='col-md-6'),
            ),
            Row(
                Column('telefono', css_class='col-md-6'),
                Column('cargo', css_class='col-md-6'),
            ),
            'avatar',
            Submit('submit', 'Guardar Cambios', css_class='btn btn-primary')
        )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario para cambiar contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'old_password',
            'new_password1',
            'new_password2',
            Submit('submit', 'Cambiar Contraseña', css_class='btn btn-primary')
        )


class CustomPasswordResetForm(PasswordResetForm):
    """Formulario para solicitar reset de contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'email',
            Submit('submit', 'Enviar Instrucciones', css_class='btn btn-primary w-100')
        )


class CustomSetPasswordForm(SetPasswordForm):
    """Formulario para establecer nueva contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'new_password1',
            'new_password2',
            Submit('submit', 'Establecer Contraseña', css_class='btn btn-primary w-100')
        )
