from django import forms
from .models import Cliente, Mascota, Cita

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        error_messages = {
            'nombre': {'required': '¡Oye! No puedes dejar a un cliente sin nombre.', 'max_length': 'El nombre es demasiado largo.'},
            'email': {'unique': 'Este correo electrónico ya está registrado.', 'invalid': 'Introduce un correo válido.'},
            'dni': {'unique': 'Ya existe un cliente con este DNI.'}
        }

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = '__all__'
        widgets = {'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})}
        error_messages = {
            'nombre': {'required': 'Toda mascota tiene un nombre, ¡escríbelo!'},
            'especie': {'invalid_choice': 'Esa especie no la atendemos.'},
            'peso': {'invalid': 'El peso debe ser un número.', 'required': 'Necesitamos saber cuánto pesa.'}
        }

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['mascota', 'veterinario', 'fecha', 'hora', 'motivo', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
        error_messages = {
            'fecha': {'required': 'Sin fecha no hay cita.', 'invalid': 'Formato de fecha incorrecto.'},
            'hora': {'required': 'Selecciona una hora para la cita.'},
            'motivo': {'required': 'Dinos qué le pasa al animalito.'}
        }