import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shambhu_pos.settings')
django.setup()

from apps.products.models import Category, Product
from apps.services.models import ServiceItem, PrinterConsumable
from apps.personal_services.models import ExpenseCategory, Expense, EMITracker
from django.utils import timezone
import datetime

print("Seeding Shambhu Gift House categories and products...")

# Categories
cat_gifts, _ = Category.objects.get_or_create(name="Gift Articles", defaults={"icon": "fa-gift", "description": "Customized gifts, photo frames, mugs & crystal items"})
cat_toys, _ = Category.objects.get_or_create(name="Toys & Games", defaults={"icon": "fa-gamepad", "description": "Remote control cars, dolls, soft toys & board games"})
cat_stationery, _ = Category.objects.get_or_create(name="School & Office Stationery", defaults={"icon": "fa-pen-ruler", "description": "Notebooks, Parker pens, geometry boxes & art supplies"})
cat_cards, _ = Category.objects.get_or_create(name="Greeting Cards & Decor", defaults={"icon": "fa-heart", "description": "Birthday cards, anniversary gifts & party decorations"})

# Products
products_data = [
    {
        "name": "Teddy Bear Soft Toy (Large 3 Feet)",
        "category": cat_toys,
        "sku": "SGH-TOY-001",
        "barcode": "890123456701",
        "cost_price": Decimal("350.00"),
        "mrp": Decimal("799.00"),
        "selling_price": Decimal("599.00"),
        "stock_quantity": 15,
        "unit": "Pcs"
    },
    {
        "name": "Personalized 3D Crystal Photo Frame with LED Base",
        "category": cat_gifts,
        "sku": "SGH-GFT-002",
        "barcode": "890123456702",
        "cost_price": Decimal("450.00"),
        "mrp": Decimal("1299.00"),
        "selling_price": Decimal("899.00"),
        "stock_quantity": 8,
        "unit": "Pcs"
    },
    {
        "name": "Parker Classic Stainless Steel Ball Pen Set",
        "category": cat_stationery,
        "sku": "SGH-STN-003",
        "barcode": "890123456703",
        "cost_price": Decimal("220.00"),
        "mrp": Decimal("450.00"),
        "selling_price": Decimal("380.00"),
        "stock_quantity": 25,
        "unit": "Box"
    },
    {
        "name": "Classmate Hardbound Register (Class 200 Pages)",
        "category": cat_stationery,
        "sku": "SGH-STN-004",
        "barcode": "890123456704",
        "cost_price": Decimal("45.00"),
        "mrp": Decimal("85.00"),
        "selling_price": Decimal("75.00"),
        "stock_quantity": 50,
        "unit": "Pcs"
    },
    {
        "name": "Remote Control Rechargeable Stunt Racing Car",
        "category": cat_toys,
        "sku": "SGH-TOY-005",
        "barcode": "890123456705",
        "cost_price": Decimal("550.00"),
        "mrp": Decimal("1499.00"),
        "selling_price": Decimal("999.00"),
        "stock_quantity": 12,
        "unit": "Pcs"
    },
    {
        "name": "Musical Birthday Snow Globe Lantern",
        "category": cat_gifts,
        "sku": "SGH-GFT-006",
        "barcode": "890123456706",
        "cost_price": Decimal("400.00"),
        "mrp": Decimal("999.00"),
        "selling_price": Decimal("749.00"),
        "stock_quantity": 10,
        "unit": "Pcs"
    },
]

for p in products_data:
    Product.objects.get_or_create(
        sku=p["sku"],
        defaults=p
    )

# Services Data
services_data = [
    {"name": "A4 Black & White Xerox", "category": "XEROX", "unit_name": "Per Page", "price": Decimal("2.00")},
    {"name": "A4 Color Printing (Laser High Quality)", "category": "PRINTING", "unit_name": "Per Page", "price": Decimal("10.00")},
    {"name": "A4 Lamination (Thick 125 Micron)", "category": "LAMINATION", "unit_name": "Per Sheet", "price": Decimal("25.00")},
    {"name": "Passport Size Photos (Set of 8 Prints)", "category": "PHOTO", "unit_name": "Per Set", "price": Decimal("50.00")},
    {"name": "Spiral Book Binding (Up to 100 Pages)", "category": "BINDING", "unit_name": "Per Book", "price": Decimal("35.00")},
]

for s in services_data:
    ServiceItem.objects.get_or_create(
        name=s["name"],
        defaults=s
    )

# Printer Consumables Data
consumables_data = [
    {
        "name": "JK Copier A4 75 GSM Paper Rim (500 Sheets)",
        "item_type": "PAPER",
        "brand_or_model": "JK Paper / Universal Xerox",
        "stock_quantity": Decimal("12.00"),
        "unit": "Rim",
        "min_stock_alert": Decimal("3.00"),
        "cost_price": Decimal("245.00"),
        "notes": "Standard A4 white paper for daily Xerox & prints"
    },
    {
        "name": "Glossy Photo Paper 180 GSM (A4 Pack of 50)",
        "item_type": "PAPER",
        "brand_or_model": "Epson / HP Photo Printers",
        "stock_quantity": Decimal("4.00"),
        "unit": "Pack",
        "min_stock_alert": Decimal("2.00"),
        "cost_price": Decimal("320.00"),
        "notes": "High gloss photo printing paper"
    },
    {
        "name": "Heavy Lamination Film Pouch 125 Micron (100 Sheets)",
        "item_type": "OTHER",
        "brand_or_model": "Standard Heat Laminator",
        "stock_quantity": Decimal("2.00"),
        "unit": "Pack",
        "min_stock_alert": Decimal("1.00"),
        "cost_price": Decimal("480.00"),
        "notes": "Clear transparent lamination pouches"
    },
    {
        "name": "Canon NPG-59 Black Toner Cartridge",
        "item_type": "INK",
        "brand_or_model": "Canon ImageRUNNER 2520 / 2525",
        "stock_quantity": Decimal("1.00"),
        "unit": "Cartridge",
        "min_stock_alert": Decimal("2.00"),
        "cost_price": Decimal("1650.00"),
        "notes": "Heavy-duty Xerox machine black toner powder"
    },
    {
        "name": "Epson 003 Genuine Black Ink Bottle (65ml)",
        "item_type": "INK",
        "brand_or_model": "Epson EcoTank L3150 / L3250",
        "stock_quantity": Decimal("3.00"),
        "unit": "Bottle",
        "min_stock_alert": Decimal("1.00"),
        "cost_price": Decimal("440.00"),
        "notes": "High yield black refill ink bottle"
    },
    {
        "name": "Epson 003 Cyan/Magenta/Yellow Ink Set (Pack of 3)",
        "item_type": "INK",
        "brand_or_model": "Epson EcoTank Color Printers",
        "stock_quantity": Decimal("2.00"),
        "unit": "Set",
        "min_stock_alert": Decimal("1.00"),
        "cost_price": Decimal("1290.00"),
        "notes": "Color refill ink bottles"
    }
]

for c in consumables_data:
    PrinterConsumable.objects.get_or_create(
        name=c["name"],
        defaults=c
    )

# Seed Expense Categories
cat_rent, _ = ExpenseCategory.objects.get_or_create(name="Store Rent & Utilities", defaults={"icon": "fa-building-user", "color_badge": "bg-primary"})
cat_bills, _ = ExpenseCategory.objects.get_or_create(name="Electricity & Water", defaults={"icon": "fa-bolt", "color_badge": "bg-warning"})
cat_snacks, _ = ExpenseCategory.objects.get_or_create(name="Tea & Refreshments", defaults={"icon": "fa-mug-hot", "color_badge": "bg-info"})
cat_salary, _ = ExpenseCategory.objects.get_or_create(name="Salary & Helper Wages", defaults={"icon": "fa-users-gear", "color_badge": "bg-success"})
cat_personal, _ = ExpenseCategory.objects.get_or_create(name="Personal & Miscellaneous", defaults={"icon": "fa-user-tag", "color_badge": "bg-purple"})
cat_emi, _ = ExpenseCategory.objects.get_or_create(name="EMI & Loan Payment", defaults={"icon": "fa-credit-card", "color_badge": "bg-danger"})

today = timezone.now().date()

# Seed Expenses
expenses_list = [
    {"title": "July Shop Monthly Rent", "category": cat_rent, "amount": Decimal("12000.00"), "expense_date": today, "payment_method": "BANK", "notes": "Paid to landlord via UPI Transfer"},
    {"title": "Monthly Electricity Bill (MSEB)", "category": cat_bills, "amount": Decimal("1850.00"), "expense_date": today, "payment_method": "UPI", "receipt_number": "ELE-88421"},
    {"title": "Staff Evening Tea & Snacks (Weekly)", "category": cat_snacks, "amount": Decimal("450.00"), "expense_date": today, "payment_method": "CASH", "notes": "Sweets and tea for helpers"},
    {"title": "Part-Time Billing Helper Salary", "category": cat_salary, "amount": Decimal("6500.00"), "expense_date": today - datetime.timedelta(days=2), "payment_method": "UPI"},
]

for exp in expenses_list:
    Expense.objects.get_or_create(
        title=exp["title"],
        expense_date=exp["expense_date"],
        defaults=exp
    )

# Seed EMI Trackers
emis_list = [
    {
        "title": "Shop Heavy Duty Canon Xerox Machine",
        "lender_name": "Bajaj Finance",
        "total_loan_amount": Decimal("60000.00"),
        "monthly_emi": Decimal("5000.00"),
        "due_day_of_month": 5,
        "tenure_months": 12,
        "paid_installments": 4,
        "status": "ACTIVE",
        "notes": "Auto-debit from HDFC Current Account on 5th of every month"
    },
    {
        "title": "Store Glass Display Refrigerator",
        "lender_name": "HDFC Consumer Durable Loan",
        "total_loan_amount": Decimal("24000.00"),
        "monthly_emi": Decimal("2000.00"),
        "due_day_of_month": 10,
        "tenure_months": 12,
        "paid_installments": 7,
        "status": "ACTIVE",
        "notes": "Display cooler for gift chocolates & soft drinks"
    },
    {
        "title": "Personal OnePlus Smartphone EMI",
        "lender_name": "ICICI Credit Card SmartEMI",
        "total_loan_amount": Decimal("36000.00"),
        "monthly_emi": Decimal("3000.00"),
        "due_day_of_month": 15,
        "tenure_months": 12,
        "paid_installments": 10,
        "status": "ACTIVE",
        "notes": "Personal phone used for WhatsApp store customer support"
    }
]

for emi in emis_list:
    EMITracker.objects.get_or_create(
        title=emi["title"],
        lender_name=emi["lender_name"],
        defaults=emi
    )

print("Demo data seeded successfully for Shambhu Gift House!")
