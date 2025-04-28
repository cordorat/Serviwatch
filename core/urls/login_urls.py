from django.urls import path
from core.views.Login.login import Login

urlpatterns = [
    path('', Login, name='login'),
]