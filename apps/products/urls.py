from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='list'),
    path('category/', views.category_list_view, name='category_save'),
    path('export/csv/', views.export_products_csv, name='export_csv'),
    path('api/search/', views.product_search_api, name='search_api'),
]
