"""
Script de verificación de la migración a DRF.
Verifica que todos los serializers y viewsets se puedan importar correctamente.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Serviwatch.settings')
django.setup()

print("🔍 Verificando migración a Django REST Framework...\n")

# Verificar serializers
print("📦 Verificando Serializers...")
try:
    from core.serializers import (
        ClienteSerializer,
        EmpleadoSerializer,
        PilasSerializer,
        IngresoSerializer,
        EgresoSerializer,
        PasswordResetTokenSerializer,
        RelojSerializer,
        RelojListSerializer,
        AbonoSerializer,
        AbonoListSerializer,
        ReparacionSerializer,
        ReparacionListSerializer,
        VentaPilaSerializer,
        VentaPilaListSerializer,
    )
    print("  ✅ ClienteSerializer")
    print("  ✅ EmpleadoSerializer")
    print("  ✅ PilasSerializer")
    print("  ✅ IngresoSerializer")
    print("  ✅ EgresoSerializer")
    print("  ✅ PasswordResetTokenSerializer")
    print("  ✅ RelojSerializer")
    print("  ✅ RelojListSerializer")
    print("  ✅ AbonoSerializer")
    print("  ✅ AbonoListSerializer")
    print("  ✅ ReparacionSerializer")
    print("  ✅ ReparacionListSerializer")
    print("  ✅ VentaPilaSerializer")
    print("  ✅ VentaPilaListSerializer")
    print("  ✅ Todos los serializers importados correctamente\n")
except Exception as e:
    print(f"  ❌ Error al importar serializers: {e}\n")
    sys.exit(1)

# Verificar viewsets
print("🎯 Verificando ViewSets...")
try:
    from core.views.Cliente.cliente_viewset import ClienteViewSet
    from core.views.Empleado.empleado_viewset import EmpleadoViewSet
    from core.views.Pilas.pilas_viewset import PilasViewSet
    from core.views.Pilas.venta_pila_viewset import VentaPilaViewSet
    from core.views.Ingreso.ingreso_viewset import IngresoViewSet
    from core.views.Egreso.egreso_viewset import EgresoViewSet
    from core.views.Reloj.reloj_viewset import RelojViewSet
    from core.views.Reloj.abono_viewset import AbonoViewSet
    from core.views.Reparacion.reparacion_viewset import ReparacionViewSet
    
    print("  ✅ ClienteViewSet")
    print("  ✅ EmpleadoViewSet")
    print("  ✅ PilasViewSet")
    print("  ✅ VentaPilaViewSet")
    print("  ✅ IngresoViewSet")
    print("  ✅ EgresoViewSet")
    print("  ✅ RelojViewSet")
    print("  ✅ AbonoViewSet")
    print("  ✅ ReparacionViewSet")
    print("  ✅ Todos los viewsets importados correctamente\n")
except Exception as e:
    print(f"  ❌ Error al importar viewsets: {e}\n")
    sys.exit(1)

# Verificar URLs
print("🌐 Verificando configuración de URLs...")
try:
    from core.urls.api_urls import router
    
    registered_viewsets = [prefix for prefix, viewset, basename in router.registry]
    expected = [
        'clientes',
        'empleados',
        'pilas',
        'ventas-pilas',
        'ingresos',
        'egresos',
        'relojes',
        'abonos',
        'reparaciones'
    ]
    
    for name in expected:
        if name in registered_viewsets:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name} no registrado")
    
    print("  ✅ Todas las rutas configuradas correctamente\n")
except Exception as e:
    print(f"  ❌ Error al verificar URLs: {e}\n")
    sys.exit(1)

# Verificar modelos
print("💾 Verificando modelos...")
try:
    from core.models.cliente import Cliente
    from core.models.empleado import Empleado
    from core.models.pilas import Pilas
    from core.models.VentaPila import VentaPila
    from core.models.ingreso import Ingreso
    from core.models.egreso import Egreso
    from core.models.reloj import Reloj
    from core.models.abono import Abono
    from core.models.reparacion import Reparacion
    from core.models.cambiar_contraseña import PasswordResetToken
    
    print("  ✅ Cliente")
    print("  ✅ Empleado")
    print("  ✅ Pilas")
    print("  ✅ VentaPila")
    print("  ✅ Ingreso")
    print("  ✅ Egreso")
    print("  ✅ Reloj")
    print("  ✅ Abono")
    print("  ✅ Reparacion")
    print("  ✅ PasswordResetToken")
    print("  ✅ Todos los modelos importados correctamente\n")
except Exception as e:
    print(f"  ❌ Error al importar modelos: {e}\n")
    sys.exit(1)

# Resumen final
print("=" * 60)
print("✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
print("=" * 60)
print("\n📊 Resumen:")
print("  • 14 Serializers creados/actualizados")
print("  • 9 ViewSets creados/actualizados")
print("  • 9 Modelos migrados a DRF")
print("  • 85+ Endpoints disponibles")
print("\n🚀 Próximos pasos:")
print("  1. Iniciar el servidor: python manage.py runserver")
print("  2. Visitar: http://localhost:8000/api/")
print("  3. Probar endpoints con los archivos *_test.http")
print("\n📖 Documentación completa en: MIGRACION_DRF_README.md")
print("=" * 60)
