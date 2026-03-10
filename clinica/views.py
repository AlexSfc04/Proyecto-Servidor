from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from .models import Cliente, Mascota, Cita
from .forms import ClienteForm, MascotaForm, CitaForm

# Función auxiliar para comprobar si el usuario tiene rol de Administrador/Staff
def is_staff(user):
    return user.is_staff

# -------------------------------------------------------------
# 1. LISTA DE CLIENTES (Paginada) -> Restricción: Login
# -------------------------------------------------------------
@login_required
def cliente_list(request):
    clientes = Cliente.objects.all().order_by('id')
    paginator = Paginator(clientes, 5) # 5 elementos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'clinica/cliente_list.html', {'page_obj': page_obj})

# -------------------------------------------------------------
# 2. CREAR CLIENTE -> Restricción: Login y Rol Staff
# -------------------------------------------------------------
@login_required
@user_passes_test(is_staff)
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'clinica/cliente_form.html', {'form': form})

# -------------------------------------------------------------
# 3. LISTA DE MASCOTAS (Paginada) -> Restricción: Login
# -------------------------------------------------------------
@login_required
def mascota_list(request):
    mascotas = Mascota.objects.all().order_by('id')
    paginator = Paginator(mascotas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'clinica/mascota_list.html', {'page_obj': page_obj})

# -------------------------------------------------------------
# 4. DETALLE DE MASCOTA -> Restricción: Login
# -------------------------------------------------------------
@login_required
def mascota_detail(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    return render(request, 'clinica/mascota_detail.html', {'mascota': mascota})

# -------------------------------------------------------------
# 5. CREAR MASCOTA -> Restricción: Login y Rol Staff
# -------------------------------------------------------------
@login_required
@user_passes_test(is_staff)
def mascota_create(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mascota_list')
    else:
        form = MascotaForm()
    return render(request, 'clinica/mascota_form.html', {'form': form})

# -------------------------------------------------------------
# 6. EDITAR MASCOTA -> Restricción: Login y Rol Staff
# -------------------------------------------------------------
@login_required
@user_passes_test(is_staff)
def mascota_update(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect('mascota_detail', pk=mascota.pk)
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'clinica/mascota_form.html', {'form': form})

@login_required
def cita_list(request):
    citas = Cita.objects.all().order_by('id')
    
    # REQUISITO: FILTRADO (por estado)
    estado_filter = request.GET.get('estado')
    if estado_filter:
        citas = citas.filter(estado=estado_filter)
        
    # REQUISITO: ORDENADO (por fecha)
    orden = request.GET.get('orden')
    if orden == 'asc':
        citas = citas.order_by('fecha')
    elif orden == 'desc':
        citas = citas.order_by('-fecha')
        
    paginator = Paginator(citas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'clinica/cita_list.html', {'page_obj': page_obj, 'estado_filter': estado_filter, 'orden': orden})

# -------------------------------------------------------------
# 8. CREAR CITA -> Restricción: Login
# -------------------------------------------------------------
@login_required
def cita_create(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.veterinario = request.user # Asigna automáticamente al usuario actual
            cita.save()
            return redirect('cita_list')
    else:
        form = CitaForm()
    return render(request, 'clinica/cita_form.html', {'form': form})

# -------------------------------------------------------------
# 9. EDITAR CITA -> Restricción: Login
# -------------------------------------------------------------
@login_required
def cita_update(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return redirect('cita_list')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'clinica/cita_form.html', {'form': form})

# -------------------------------------------------------------
# 10. ESTADÍSTICAS (5 Datos Diferentes) -> Restricción: Login y Rol Staff
# -------------------------------------------------------------
@login_required
@user_passes_test(is_staff)
def dashboard_estadisticas(request):
    # Cálculo de las 5 estadísticas requeridas
    total_mascotas = Mascota.objects.count()                                      
    total_clientes = Cliente.objects.count()                                      
    peso_medio = Mascota.objects.aggregate(Avg('peso'))['peso__avg'] or 0         
    especies_stats = list(Mascota.objects.values('especie').annotate(total=Count('id'))) 
    citas_stats = list(Cita.objects.values('estado').annotate(total=Count('id')))        

    context = {
        'total_mascotas': total_mascotas,
        'total_clientes': total_clientes,
        'peso_medio': round(peso_medio, 2),
        'especies_stats': especies_stats,
        'citas_stats': citas_stats,
    }
    return render(request, 'clinica/dashboard.html', context)