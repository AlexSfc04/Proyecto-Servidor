from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
import re

# --- VALIDACIONES ---
def validar_dni(value):
    if not re.match(r'^\d{8}[A-Z]$', value): raise ValidationError('El DNI debe tener 8 números y una letra mayúscula.')
def validar_telefono(value):
    if not re.match(r'^\d{9}$', value): raise ValidationError('El teléfono debe tener exactamente 9 dígitos.')
def validar_mayoria_edad(value):
    if value < 18: raise ValidationError('El cliente debe ser mayor de edad (18+).')
def validar_fecha_pasada(value):
    if value > date.today(): raise ValidationError('La fecha de nacimiento no puede estar en el futuro.')
def validar_peso_positivo(value):
    if value <= 0: raise ValidationError('El peso debe ser mayor a 0 kg.')
def validar_fecha_futura(value):
    if value < date.today(): raise ValidationError('La cita no puede ser en una fecha pasada.')
def validar_longitud_motivo(value):
    if len(value) < 10: raise ValidationError('El motivo de la consulta debe tener al menos 10 caracteres.')

# --- MODELOS ---
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=9, unique=True, validators=[validar_dni])
    telefono = models.CharField(max_length=9, validators=[validar_telefono])
    edad = models.IntegerField(validators=[validar_mayoria_edad])
    email = models.EmailField(unique=True)

    def __str__(self): return f"{self.nombre} ({self.dni})"

class Mascota(models.Model):
    ESPECIES = [('Perro', 'Perro'), ('Gato', 'Gato'), ('Ave', 'Ave'), ('Exotico', 'Exótico')]
    nombre = models.CharField(max_length=50)
    especie = models.CharField(max_length=20, choices=ESPECIES)
    peso = models.DecimalField(max_digits=5, decimal_places=2, validators=[validar_peso_positivo])
    fecha_nacimiento = models.DateField(validators=[validar_fecha_pasada])
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='mascotas')

    def __str__(self): return f"{self.nombre} - {self.especie}"

class Cita(models.Model):
    ESTADOS = [('Pendiente', 'Pendiente'), ('Completada', 'Completada'), ('Cancelada', 'Cancelada')]
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas')
    veterinario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(validators=[validar_fecha_futura])
    hora = models.TimeField()
    motivo = models.TextField(validators=[validar_longitud_motivo])
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')

    def __str__(self): return f"Cita: {self.mascota.nombre} el {self.fecha}"