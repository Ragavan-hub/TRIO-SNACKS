"""
PDF invoice generation using ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
from io import BytesIO
from models import Setting

def get_setting(key, default_value):
    """Get setting value from database"""
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        return setting.value
    return default_value

def generate_invoice_pdf(order):
    """Generate PDF invoice for an order"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    
    # Get shop settings
    shop_name = get_setting('shop_name', 'Trio Snacks')
    shop_address = get_setting('shop_address', '')
    shop_phone = get_setting('shop_phone', '')
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    # Shop Header
    elements.append(Paragraph(shop_name, title_style))
    if shop_address:
        elements.append(Paragraph(shop_address, styles['Normal']))
    if shop_phone:
        elements.append(Paragraph(f"Phone: {shop_phone}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Invoice Details
    invoice_data = [
        ['Invoice Number:', order.invoice_number],
        ['Date:', order.created_at.strftime('%d-%m-%Y %H:%M:%S')],
    ]
    
    invoice_table = Table(invoice_data, colWidths=[80*mm, 100*mm])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Customer Details removed
    
    # Items Table
    elements.append(Paragraph("Items", heading_style))
    
    items_data = [['S.No', 'Item', 'Qty', 'Unit Price', 'Total']]
    
    for idx, item in enumerate(order.items, 1):
        items_data.append([
            str(idx),
            item.product.name,
            str(item.quantity),
            f"₹{item.unit_price:.2f}",
            f"₹{item.total_price:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[15*mm, 80*mm, 25*mm, 35*mm, 35*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals (tax removed)
    totals_data = [
        ['Subtotal:', f"₹{order.subtotal:.2f}"],
    ]
    
    if order.discount_amount > 0:
        totals_data.append(['Discount:', f"-₹{order.discount_amount:.2f}"])
    
    totals_data.append(['Total Amount:', f"₹{order.total_amount:.2f}"])
    
    totals_table = Table(totals_data, colWidths=[120*mm, 60*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#FF6B35')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_text = get_setting('invoice_footer', 'Thank you for your business!')
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

