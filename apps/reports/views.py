from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal
from apps.products.models import Product, Category
from apps.billing.models import Invoice, InvoiceItem
from apps.customers.models import Customer
from apps.authentication.models import AuditLog

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    today_invoices = Invoice.objects.filter(created_at__date=today)
    today_revenue = today_invoices.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    today_sales_count = today_invoices.count()

    monthly_invoices = Invoice.objects.filter(created_at__date__gte=start_of_month)
    monthly_revenue = monthly_invoices.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')

    total_products = Product.objects.filter(is_active=True).count()
    low_stock_count = sum(1 for p in Product.objects.filter(is_active=True) if p.is_low_stock)

    recent_invoices = Invoice.objects.select_related('billed_by')[:8]
    recent_logs = AuditLog.objects.select_related('user')[:8]
    total_khata = Customer.objects.aggregate(total=Sum('outstanding_balance'))['total'] or Decimal('0.00')

    context = {
        'today_revenue': today_revenue,
        'today_sales_count': today_sales_count,
        'monthly_revenue': monthly_revenue,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_khata': total_khata,
        'recent_invoices': recent_invoices,
        'recent_logs': recent_logs,
    }
    return render(request, 'dashboard.html', context)


@login_required
def reports_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    invoices = Invoice.objects.all()
    if start_date:
        invoices = invoices.filter(created_at__date__gte=start_date)
    if end_date:
        invoices = invoices.filter(created_at__date__lte=end_date)

    total_sales = invoices.aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    total_gst = invoices.aggregate(total=Sum('gst_amount'))['total'] or Decimal('0.00')
    total_discount = invoices.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')

    cash_sales = invoices.filter(payment_mode='CASH').aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    upi_sales = invoices.filter(payment_mode='UPI').aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')
    khata_sales = invoices.filter(payment_mode='KHATA').aggregate(total=Sum('grand_total'))['total'] or Decimal('0.00')

    context = {
        'invoices': invoices[:50],
        'total_sales': total_sales,
        'total_gst': total_gst,
        'total_discount': total_discount,
        'cash_sales': cash_sales,
        'upi_sales': upi_sales,
        'khata_sales': khata_sales,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'reports.html', context)
