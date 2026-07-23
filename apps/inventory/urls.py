from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list_view, name='list'),
]
