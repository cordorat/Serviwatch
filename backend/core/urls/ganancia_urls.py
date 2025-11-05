from django.urls import path
from core.views.Ganancia.ganancia_view import ganancia_view, reporte_ganancias_pdf

urlpatterns = [
    path('contable/ganancia/', ganancia_view, name='ganancia'),
    path('contable/ganancia/reporte/', reporte_ganancias_pdf, name='reporte_ganancias_pdf'),
]




