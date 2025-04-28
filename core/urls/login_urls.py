from django.urls import path
from core.views.login.login_view import login_view

urlpatterns = [
    path('', login_view, name='login'),
]