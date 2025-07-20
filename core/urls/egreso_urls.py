from django.urls import path
from core.views.Egreso.egreso_view import egreso_view
from core.views.Egreso.confirmar_egreso_view import confirmar_egreso_view
from core.views.Egreso.reporte_egreso_view import reporte_egresos_pdf, reporte_egresos_form

urlpatterns = [
    path('contable/egreso/', egreso_view, name='egreso'),
    path('contable/egreso/confirmar/', confirmar_egreso_view, name='confirmar_egreso'),
    path('contable/egreso/reporte/', reporte_egresos_pdf, name='reporte_egresos_pdf'),
    path('contable/egreso/reporte-form/', reporte_egresos_form, name='reporte_egresos_form'),
]