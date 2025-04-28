from django.urls import path
from core.views.login.login import Login

urlpatterns = [
    path('', Login, name='login'),
]