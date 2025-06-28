from django.urls import path
from core.views.Ganancia.ganancia_view import ganancia_view

urlpatterns = [
    path('contabilidad/ganancia/', ganancia_view, name='ganancia'),
]




