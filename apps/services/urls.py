from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list_view, name='list'),
    path('recharge/', views.recharge_view, name='recharge'),
]

