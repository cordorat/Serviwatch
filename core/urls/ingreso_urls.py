from django.urls import path
from core.views.Ingreso.ingreso_view import ingreso_view
from core.views.Ingreso.confirmar_ingreso_view import confirmar_ingreso_view
from core.views.Ingreso.reporte_ingreso_view import reporte_ingresos_pdf, reporte_ingresos_form

urlpatterns = [
    path('contable/ingreso/', ingreso_view, name='ingreso'),
    path('contable/ingreso/confirmar/', confirmar_ingreso_view, name='confirmar_ingreso'),
    path('contable/ingreso/reporte/', reporte_ingresos_pdf, name='reporte_ingresos_pdf'),
    path('contable/ingreso/reporte-form/', reporte_ingresos_form, name='reporte_ingresos_form'),
]