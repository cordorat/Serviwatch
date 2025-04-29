from django.urls import path
from core.views.Logout.logout_view import logout_view

urlpatterns = [
    path('logout/', logout_view, name='logout'),
]