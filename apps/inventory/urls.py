from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list_view, name='list'),
    path('spending/', views.stock_spending_list_view, name='spending_list'),
    path('spending/export/', views.export_spending_csv, name='spending_export'),
]

