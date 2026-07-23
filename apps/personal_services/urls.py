from django.urls import path
from . import views

app_name = 'personal_services'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('expense/add/', views.add_expense, name='add_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('emi/add/', views.add_emi, name='add_emi'),
    path('emi/delete/<int:pk>/', views.delete_emi, name='delete_emi'),
    path('emi/pay/<int:pk>/', views.pay_emi_installment, name='pay_emi_installment'),
]
