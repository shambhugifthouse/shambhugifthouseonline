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
    path('profit-report/', views.profit_report_view, name='profit_report'),
    path('profit-report/pdf/download/', views.download_profit_pdf, name='download_profit_pdf'),
    path('profit-report/pdf/send-email/', views.send_profit_pdf_email_view, name='send_profit_pdf_email'),
]
