from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Cliente, Mascota, Cita
from .forms import ClienteForm, MascotaForm, CitaForm

class ClinicaTests(TestCase):
    def setUp(self):
        # 1. PREPARACIÓN DE DATOS (Usuarios, Clientes y Mascotas base)
        self.user_normal = User.objects.create_user(username='veterinario', password='password123')
        self.user_staff = User.objects.create_user(username='admin', password='password123', is_staff=True)
        
        self.cliente = Cliente.objects.create(nombre="Ana García", dni="12345678A", telefono="600123456", edad=30, email="ana@email.com")
        self.mascota = Mascota.objects.create(nombre="Toby", especie="Perro", peso=10.5, fecha_nacimiento=date.today() - timedelta(days=365), cliente=self.cliente)
        self.cita = Cita.objects.create(mascota=self.mascota, veterinario=self.user_normal, fecha=date.today() + timedelta(days=1), hora="10:00", motivo="Revisión general anual", estado="Pendiente")

    # --- Modelo Cliente ---
    def test_modelo_cliente_valido(self):
        cliente = Cliente(nombre="Luis", dni="87654321B", telefono="611222333", edad=40, email="luis@email.com")
        cliente.full_clean() # Pasa sin errores
        self.assertTrue(True)

    def test_modelo_cliente_dni_invalido(self):
        cliente = Cliente(nombre="Luis", dni="123", telefono="611222333", edad=40, email="luis2@email.com")
        with self.assertRaises(ValidationError): cliente.full_clean()

    def test_modelo_cliente_telefono_invalido(self):
        cliente = Cliente(nombre="Luis", dni="87654321B", telefono="hola", edad=40, email="luis3@email.com")
        with self.assertRaises(ValidationError): cliente.full_clean()

    def test_modelo_cliente_menor_edad(self):
        cliente = Cliente(nombre="Luis", dni="87654321B", telefono="611222333", edad=15, email="luis4@email.com")
        with self.assertRaises(ValidationError): cliente.full_clean()

    def test_modelo_cliente_email_duplicado(self):
        cliente = Cliente(nombre="Otro", dni="99999999Z", telefono="699999999", edad=50, email="ana@email.com")
        with self.assertRaises(ValidationError): cliente.full_clean()

    # --- Modelo Mascota ---
    def test_modelo_mascota_valido(self):
        mascota = Mascota(nombre="Luna", especie="Gato", peso=4.0, fecha_nacimiento=date(2020, 1, 1), cliente=self.cliente)
        mascota.full_clean()
        self.assertTrue(True)

    def test_modelo_mascota_peso_negativo(self):
        mascota = Mascota(nombre="Luna", especie="Gato", peso=-2.0, fecha_nacimiento=date(2020, 1, 1), cliente=self.cliente)
        with self.assertRaises(ValidationError): mascota.full_clean()

    def test_modelo_mascota_fecha_futura(self):
        mascota = Mascota(nombre="Luna", especie="Gato", peso=4.0, fecha_nacimiento=date.today() + timedelta(days=10), cliente=self.cliente)
        with self.assertRaises(ValidationError): mascota.full_clean()

    def test_modelo_mascota_especie_invalida(self):
        mascota = Mascota(nombre="Luna", especie="Dragon", peso=4.0, fecha_nacimiento=date(2020, 1, 1), cliente=self.cliente)
        with self.assertRaises(ValidationError): mascota.full_clean()

    def test_modelo_mascota_sin_cliente(self):
        mascota = Mascota(nombre="Luna", especie="Gato", peso=4.0, fecha_nacimiento=date(2020, 1, 1))
        with self.assertRaises(ValidationError): mascota.full_clean()

    # --- Modelo Cita ---
    def test_modelo_cita_valida(self):
        cita = Cita(mascota=self.mascota, veterinario=self.user_normal, fecha=date.today() + timedelta(days=5), hora="12:00", motivo="Vacuna antirrábica")
        cita.full_clean()
        self.assertTrue(True)

    def test_modelo_cita_fecha_pasada(self):
        cita = Cita(mascota=self.mascota, fecha=date.today() - timedelta(days=5), hora="12:00", motivo="Vacuna antirrábica")
        with self.assertRaises(ValidationError): cita.full_clean()

    def test_modelo_cita_motivo_corto(self):
        cita = Cita(mascota=self.mascota, fecha=date.today() + timedelta(days=5), hora="12:00", motivo="Corta")
        with self.assertRaises(ValidationError): cita.full_clean()

    def test_modelo_cita_estado_invalido(self):
        cita = Cita(mascota=self.mascota, fecha=date.today() + timedelta(days=5), hora="12:00", motivo="Vacunación anual", estado="Inventado")
        with self.assertRaises(ValidationError): cita.full_clean()

    def test_modelo_cita_sin_mascota(self):
        cita = Cita(fecha=date.today() + timedelta(days=5), hora="12:00", motivo="Vacuna antirrábica")
        with self.assertRaises(ValidationError): cita.full_clean()

    # --- Formularios Cliente ---
    def test_form_cliente_valido(self):
        form = ClienteForm(data={'nombre': 'Carlos', 'dni': '11111111H', 'telefono': '655555555', 'edad': 25, 'email': 'carlos@email.com'})
        self.assertTrue(form.is_valid())

    def test_form_cliente_sin_nombre(self):
        form = ClienteForm(data={'dni': '11111111H', 'telefono': '655555555', 'edad': 25, 'email': 'carlos@email.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['nombre'][0], '¡Oye! No puedes dejar a un cliente sin nombre.')

    def test_form_cliente_dni_duplicado(self):
        form = ClienteForm(data={'nombre': 'Carlos', 'dni': '12345678A', 'telefono': '655555555', 'edad': 25, 'email': 'carlos@email.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['dni'][0], 'Ya existe un cliente con este DNI.')

    def test_form_cliente_email_invalido(self):
        form = ClienteForm(data={'nombre': 'Carlos', 'dni': '11111111H', 'telefono': '655555555', 'edad': 25, 'email': 'correo_raro'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'Introduce un correo válido.')

    def test_form_cliente_email_duplicado(self):
        form = ClienteForm(data={'nombre': 'Carlos', 'dni': '11111111H', 'telefono': '655555555', 'edad': 25, 'email': 'ana@email.com'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'][0], 'Este correo electrónico ya está registrado.')

    # --- Formularios Mascota ---
    def test_form_mascota_valido(self):
        form = MascotaForm(data={'nombre': 'Kira', 'especie': 'Perro', 'peso': 5, 'fecha_nacimiento': date.today() - timedelta(days=100), 'cliente': self.cliente.pk})
        self.assertTrue(form.is_valid())

    def test_form_mascota_sin_nombre(self):
        form = MascotaForm(data={'especie': 'Perro', 'peso': 5, 'fecha_nacimiento': date.today(), 'cliente': self.cliente.pk})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['nombre'][0], 'Toda mascota tiene un nombre, ¡escríbelo!')

    def test_form_mascota_especie_invalida(self):
        form = MascotaForm(data={'nombre': 'Kira', 'especie': 'Pez', 'peso': 5, 'fecha_nacimiento': date.today(), 'cliente': self.cliente.pk})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['especie'][0], 'Esa especie no la atendemos.')

    def test_form_mascota_sin_peso(self):
        form = MascotaForm(data={'nombre': 'Kira', 'especie': 'Perro', 'fecha_nacimiento': date.today(), 'cliente': self.cliente.pk})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['peso'][0], 'Necesitamos saber cuánto pesa.')

    def test_form_mascota_peso_texto(self):
        form = MascotaForm(data={'nombre': 'Kira', 'especie': 'Perro', 'peso': 'cinco', 'fecha_nacimiento': date.today(), 'cliente': self.cliente.pk})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['peso'][0], 'El peso debe ser un número.')

    # --- Formularios Cita ---
    def test_form_cita_valido(self):
        form = CitaForm(data={'mascota': self.mascota.pk, 'veterinario': self.user_normal.pk, 'fecha': date.today() + timedelta(days=2), 'hora': '10:00', 'motivo': 'Revisión orejas', 'estado': 'Pendiente'})
        self.assertTrue(form.is_valid())

    def test_form_cita_sin_fecha(self):
        form = CitaForm(data={'mascota': self.mascota.pk, 'hora': '10:00', 'motivo': 'Revisión orejas', 'estado': 'Pendiente'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['fecha'][0], 'Sin fecha no hay cita.')

    def test_form_cita_fecha_invalida(self):
        form = CitaForm(data={'mascota': self.mascota.pk, 'fecha': 'fecha_falsa', 'hora': '10:00', 'motivo': 'Revisión orejas', 'estado': 'Pendiente'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['fecha'][0], 'Formato de fecha incorrecto.')

    def test_form_cita_sin_hora(self):
        form = CitaForm(data={'mascota': self.mascota.pk, 'fecha': date.today() + timedelta(days=2), 'motivo': 'Revisión orejas', 'estado': 'Pendiente'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['hora'][0], 'Selecciona una hora para la cita.')

    def test_form_cita_sin_motivo(self):
        form = CitaForm(data={'mascota': self.mascota.pk, 'fecha': date.today() + timedelta(days=2), 'hora': '10:00', 'estado': 'Pendiente'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['motivo'][0], 'Dinos qué le pasa al animalito.')

    def check_unlogged_redirect(self, url_name, kwargs=None):
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Verifica que expulsa al usuario no logeado
        self.assertTrue(response.url.startswith('/accounts/login/'))

    # 1. cliente_list
    def test_view_cliente_list_sin_logear(self): self.check_unlogged_redirect('cliente_list')
    def test_view_cliente_list_logeado_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('cliente_list'))
        self.assertEqual(response.status_code, 200)

    # 2. cliente_create
    def test_view_cliente_create_sin_logear(self): self.check_unlogged_redirect('cliente_create')
    def test_view_cliente_create_logeado_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('cliente_create'))
        self.assertEqual(response.status_code, 200)

    # 3. mascota_list
    def test_view_mascota_list_sin_logear(self): self.check_unlogged_redirect('mascota_list')
    def test_view_mascota_list_logeado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(reverse('mascota_list'))
        self.assertEqual(response.status_code, 200)

    # 4. mascota_detail
    def test_view_mascota_detail_sin_logear(self): self.check_unlogged_redirect('mascota_detail', kwargs={'pk': self.mascota.pk})
    def test_view_mascota_detail_logeado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(reverse('mascota_detail', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(response.status_code, 200)

    # 5. mascota_create
    def test_view_mascota_create_sin_logear(self): self.check_unlogged_redirect('mascota_create')
    def test_view_mascota_create_logeado_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('mascota_create'))
        self.assertEqual(response.status_code, 200)

    # 6. mascota_update
    def test_view_mascota_update_sin_logear(self): self.check_unlogged_redirect('mascota_update', kwargs={'pk': self.mascota.pk})
    def test_view_mascota_update_logeado_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('mascota_update', kwargs={'pk': self.mascota.pk}))
        self.assertEqual(response.status_code, 200)

    # 7. cita_list
    def test_view_cita_list_sin_logear(self): self.check_unlogged_redirect('cita_list')
    def test_view_cita_list_logeado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(reverse('cita_list'))
        self.assertEqual(response.status_code, 200)

    # 8. cita_create
    def test_view_cita_create_sin_logear(self): self.check_unlogged_redirect('cita_create')
    def test_view_cita_create_logeado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(reverse('cita_create'))
        self.assertEqual(response.status_code, 200)

    # 9. cita_update
    def test_view_cita_update_sin_logear(self): self.check_unlogged_redirect('cita_update', kwargs={'pk': self.cita.pk})
    def test_view_cita_update_logeado(self):
        self.client.force_login(self.user_normal)
        response = self.client.get(reverse('cita_update', kwargs={'pk': self.cita.pk}))
        self.assertEqual(response.status_code, 200)

    # 10. dashboard
    def test_view_dashboard_sin_logear(self): self.check_unlogged_redirect('dashboard')
    def test_view_dashboard_logeado_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)