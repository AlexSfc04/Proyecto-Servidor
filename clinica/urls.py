from django.urls import path
from . import views

urlpatterns = [
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    
    path('mascotas/', views.mascota_list, name='mascotas_list'), 
    path('mascotas/lista/', views.mascota_list, name='mascota_list'),
    path('mascotas/<int:pk>/', views.mascota_detail, name='mascota_detail'),
    path('mascotas/nueva/', views.mascota_create, name='mascota_create'),
    path('mascotas/<int:pk>/editar/', views.mascota_update, name='mascota_update'),
    
    path('citas/', views.cita_list, name='cita_list'),
    path('citas/nueva/', views.cita_create, name='cita_create'),
    path('citas/<int:pk>/editar/', views.cita_update, name='cita_update'),
    
    path('dashboard/', views.dashboard_estadisticas, name='dashboard'),
]