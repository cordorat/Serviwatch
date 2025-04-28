from django.urls import path
from core.views.login.login_view import Login

urlpatterns = [
    path('', Login, name='login'),
]