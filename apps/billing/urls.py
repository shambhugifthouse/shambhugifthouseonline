from django.urls import path
from . import views

urlpatterns = [
    path('', views.billing_pos_view, name='pos'),
    path('checkout/', views.process_checkout_api, name='checkout'),
    path('invoice/<int:pk>/', views.invoice_detail_view, name='detail'),
    path('invoice/<int:pk>/print/', views.invoice_print_view, name='print'),
]
