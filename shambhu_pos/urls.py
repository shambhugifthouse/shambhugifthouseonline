from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.products.views import public_store_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', public_store_view, name='store_home'),
    path('dashboard/', include(('apps.reports.urls', 'dashboard'), namespace='dashboard')),
    path('auth/', include(('apps.authentication.urls', 'auth'), namespace='auth')),
    path('products/', include(('apps.products.urls', 'products'), namespace='products')),
    path('inventory/', include(('apps.inventory.urls', 'inventory'), namespace='inventory')),
    path('billing/', include(('apps.billing.urls', 'billing'), namespace='billing')),
    path('services/', include(('apps.services.urls', 'services'), namespace='services')),
    path('customers/', include(('apps.customers.urls', 'customers'), namespace='customers')),
    path('suppliers/', include(('apps.suppliers.urls', 'suppliers'), namespace='suppliers')),
    path('reports/', include(('apps.reports.urls', 'reports'), namespace='reports')),
    path('personal-services/', include(('apps.personal_services.urls', 'personal_services'), namespace='personal_services')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
