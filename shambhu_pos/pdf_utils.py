import io
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from apps.billing.models import Invoice
from apps.services.models import RechargeTransaction, OtherServiceTransaction
from apps.personal_services.models import Expense, ExpenseCategory, EMITracker, EMIPayment


def generate_financial_pdf_report(start_date=None, end_date=None):
    """
    Generates a professional PDF Financial & Overall Profit Statement for Shambhu Gift House.
    Returns bytes of the generated PDF file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    elements = []
    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_COLOR = colors.HexColor('#09241B')    # Dark Forest Green
    GOLD_COLOR = colors.HexColor('#D97706')       # Warm Metallic Gold
    TEXT_COLOR = colors.HexColor('#1E293B')       # Slate Dark
    LIGHT_BG = colors.HexColor('#F8FAFC')         # Soft Gray

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY_COLOR,
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )
    section_heading = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=14,
        spaceAfter=6
    )
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=TEXT_COLOR)
    cell_bold = ParagraphStyle('CellB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=PRIMARY_COLOR)
    cell_right_bold = ParagraphStyle('CellRB', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=PRIMARY_COLOR, alignment=2)
    cell_right = ParagraphStyle('CellR', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=TEXT_COLOR, alignment=2)

    # 1. Header Banner
    now = timezone.now()
    elements.append(Paragraph("🎁 SHAMBHU GIFT HOUSE", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Comprehensive Financial & Overall Profit Statement", subtitle_style))
    elements.append(Paragraph(f"Generated On: {now.strftime('%B %d, %Y - %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=GOLD_COLOR, spaceBefore=4, spaceAfter=14))

    # 2. Gather Data Metrics
    # Filter queryset by dates if provided
    inv_qs = Invoice.objects.all()
    rech_qs = RechargeTransaction.objects.filter(status='SUCCESS')
    oth_qs = OtherServiceTransaction.objects.all()
    exp_qs = Expense.objects.all()

    if start_date:
        inv_qs = inv_qs.filter(created_at__date__gte=start_date)
        rech_qs = rech_qs.filter(created_at__date__gte=start_date)
        oth_qs = oth_qs.filter(created_at__date__gte=start_date)
        exp_qs = exp_qs.filter(expense_date__gte=start_date)
    if end_date:
        inv_qs = inv_qs.filter(created_at__date__lte=end_date)
        rech_qs = rech_qs.filter(created_at__date__lte=end_date)
        oth_qs = oth_qs.filter(created_at__date__lte=end_date)
        exp_qs = exp_qs.filter(expense_date__lte=end_date)

    total_pos_sales = inv_qs.aggregate(t=Sum('grand_total'))['t'] or Decimal('0.00')
    total_recharge_vol = rech_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    total_recharge_comm = rech_qs.aggregate(t=Sum('commission'))['t'] or Decimal('0.00')
    total_other_services_charge = oth_qs.aggregate(t=Sum('service_charge'))['t'] or Decimal('0.00')
    
    total_revenue = total_pos_sales + total_recharge_comm + total_other_services_charge

    total_expenses = exp_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    
    emis = EMITracker.objects.all()
    active_emis = emis.filter(status='ACTIVE')
    monthly_emi_commitment = active_emis.aggregate(t=Sum('monthly_emi'))['t'] or Decimal('0.00')
    total_emi_paid = EMIPayment.objects.aggregate(t=Sum('amount_paid'))['t'] or Decimal('0.00')

    net_overall_profit = total_revenue - total_expenses - total_emi_paid

    # 3. Overall KPI Summary Table
    elements.append(Paragraph("📊 Key Financial Summary", section_heading))
    kpi_data = [
        [Paragraph("Metric Description", cell_bold), Paragraph("Amount (₹)", cell_right_bold)],
        [Paragraph("Total POS & Retail Invoices Sales", cell_style), Paragraph(f"₹ {total_pos_sales:,.2f}", cell_right)],
        [Paragraph("Total Recharge Commission Earned", cell_style), Paragraph(f"₹ {total_recharge_comm:,.2f}", cell_right)],
        [Paragraph("Total Personal Services & Filing Charges", cell_style), Paragraph(f"₹ {total_other_services_charge:,.2f}", cell_right)],
        [Paragraph("TOTAL GROSS REVENUE", cell_bold), Paragraph(f"₹ {total_revenue:,.2f}", cell_right_bold)],
        [Paragraph("Total Personal & Shop Expenses", cell_style), Paragraph(f"- ₹ {total_expenses:,.2f}", cell_right)],
        [Paragraph("Total EMI & Loan Installments Paid", cell_style), Paragraph(f"- ₹ {total_emi_paid:,.2f}", cell_right)],
        [Paragraph("NET OVERALL PROFIT", cell_bold), Paragraph(f"₹ {net_overall_profit:,.2f}", cell_right_bold)],
    ]
    t_kpi = Table(kpi_data, colWidths=[340, 180])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#09241B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#FEF3C7')), # Revenue Highlight
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#D1FAE5')), # Net Profit Highlight
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 14))

    # 4. Expense Breakdown by Category
    elements.append(Paragraph("💸 Personal & Shop Expenses by Category", section_heading))
    cat_expenses = ExpenseCategory.objects.all()
    exp_cat_data = [[Paragraph("Category Name", cell_bold), Paragraph("Expense Count", cell_style), Paragraph("Total Amount (₹)", cell_right_bold)]]
    
    for cat in cat_expenses:
        c_qs = exp_qs.filter(category=cat)
        c_amt = c_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        c_cnt = c_qs.count()
        if c_cnt > 0:
            exp_cat_data.append([
                Paragraph(cat.name, cell_style),
                Paragraph(str(c_cnt), cell_style),
                Paragraph(f"₹ {c_amt:,.2f}", cell_right)
            ])

    # Uncategorized
    uncat_qs = exp_qs.filter(category__isnull=True)
    uncat_amt = uncat_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    if uncat_qs.count() > 0:
        exp_cat_data.append([
            Paragraph("Uncategorized General Expenses", cell_style),
            Paragraph(str(uncat_qs.count()), cell_style),
            Paragraph(f"₹ {uncat_amt:,.2f}", cell_right)
        ])

    exp_cat_data.append([
        Paragraph("TOTAL EXPENSES", cell_bold),
        Paragraph(str(exp_qs.count()), cell_bold),
        Paragraph(f"₹ {total_expenses:,.2f}", cell_right_bold)
    ])

    t_exp = Table(exp_cat_data, colWidths=[260, 100, 160])
    t_exp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
    ]))
    elements.append(t_exp)
    elements.append(Spacer(1, 14))

    # 5. Active EMI & Loan Trackers
    elements.append(Paragraph("🏦 Active EMI Loans & Monthly Commitments", section_heading))
    emi_data = [[
        Paragraph("Lender & Item Title", cell_bold),
        Paragraph("Monthly EMI", cell_right_bold),
        Paragraph("Tenure / Paid", cell_style),
        Paragraph("Remaining Balance", cell_right_bold)
    ]]

    for emi in active_emis:
        emi_data.append([
            Paragraph(f"<b>{emi.title}</b><br/><font color='#64748b'>{emi.lender_name}</font>", cell_style),
            Paragraph(f"₹ {emi.monthly_emi:,.2f}", cell_right),
            Paragraph(f"{emi.paid_installments} / {emi.tenure_months} Mo", cell_style),
            Paragraph(f"₹ {emi.remaining_balance:,.2f}", cell_right)
        ])

    if not active_emis.exists():
        emi_data.append([Paragraph("No active EMI loans found.", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style), Paragraph("-", cell_style)])
    else:
        emi_data.append([
            Paragraph("TOTAL MONTHLY COMMITMENT", cell_bold),
            Paragraph(f"₹ {monthly_emi_commitment:,.2f}", cell_right_bold),
            Paragraph(f"{active_emis.count()} Active Loans", cell_bold),
            Paragraph("-", cell_right)
        ])

    t_emi = Table(emi_data, colWidths=[200, 110, 100, 110])
    t_emi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F8FAFC')),
    ]))
    elements.append(t_emi)

    # 6. Footer Signature
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=5, spaceAfter=10))
    footer_text = Paragraph(
        "© 2026 Shambhu Gift House • Dhandarphal Bk, Sangamner • Contact: 8975027902 / 9139090903<br/>"
        "<i>Confidential Automated Financial Statement. Generated via POS Cloud Management System.</i>",
        subtitle_style
    )
    elements.append(footer_text)

    # Build PDF Document
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
