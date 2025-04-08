from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from core.models import Cliente
from core.forms import ClienteForm

class ClienteListView(ListView):
    model = Cliente
    template_name = 'cliente/cliente_list.html'
    context_object_name = 'clientes'

class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/cliente_form.html'
    success_url = reverse_lazy('cliente_list')