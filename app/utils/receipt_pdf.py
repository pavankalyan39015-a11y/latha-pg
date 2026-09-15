import io
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

def generate_receipt_pdf_bytes(receipt_data: dict) -> bytes:
    buffer = io.BytesIO()
    # A5 size (148 x 210 mm) is ideal for receipts
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A5,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'ReceiptSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        alignment=0
    )

    badge_style = ParagraphStyle(
        'ReceiptBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#059669'),
        alignment=2
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569')
    )

    val_style = ParagraphStyle(
        'ValStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # 1. Header Table (Brand on Left, Status Badge on Right)
    brand_text = f"<b>LATHA PG FOR GENTS</b><br/><font size='8' color='#6366f1'>Safe Stay, Better Study &bull; 2, 3, 4 Sharing with Attached Bath</font><br/><font size='7.5' color='#64748b'>Helplines: 9353439703 / 9019870803</font>"
    badge_text = f"<font size='10' color='#059669'><b>[ PAID &amp; VERIFIED ]</b></font><br/><font size='8' color='#64748b'><b>Receipt:</b> {receipt_data.get('receipt_number', 'N/A')}</font><br/><font size='7.5' color='#64748b'><b>Date:</b> {receipt_data.get('payment_date', 'N/A')}</font>"

    header_table = Table(
        [[Paragraph(brand_text, title_style), Paragraph(badge_text, badge_style)]],
        colWidths=[80 * mm, 44 * mm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=4 * mm))

    # 2. Resident Details Card Table
    tenant_name = receipt_data.get('tenant_name', 'Guest')
    tenant_phone = receipt_data.get('tenant_phone', 'N/A')
    room_num = receipt_data.get('room_number', 'N/A')
    bed_num = receipt_data.get('bed_number', 'N/A')
    pay_mode = receipt_data.get('payment_method', 'UPI')
    txn_ref = receipt_data.get('transaction_reference', 'N/A')
    amount_val = receipt_data.get('amount', 0.0)

    details_data = [
        [
            Paragraph("<b>RECEIVED FROM:</b>", bold_label),
            Paragraph("<b>ALLOCATED ACCOMMODATION:</b>", bold_label)
        ],
        [
            Paragraph(f"<b>{tenant_name}</b><br/><font size='8' color='#64748b'>Mobile: {tenant_phone}</font>", val_style),
            Paragraph(f"<b>Room {room_num}</b> (Bed: {bed_num})<br/><font size='8' color='#64748b'>Attached Bathroom</font>", val_style)
        ]
    ]

    details_table = Table(details_data, colWidths=[62 * mm, 62 * mm])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 4 * mm))

    # 3. Line Items Table (Description & Amount)
    notes_val = receipt_data.get('notes', 'Monthly Rent & Accommodation Maintenance')
    items_data = [
        [Paragraph("<b>Description / Particulars</b>", bold_label), Paragraph("<b>Amount (INR)</b>", badge_style)],
        [
            Paragraph(f"<b>{notes_val}</b><br/><font size='7.5' color='#64748b'>Includes: Room stay, Wi-Fi, CCTV, Washing Machine, Power Backup</font>", val_style),
            Paragraph(f"<b>Rs. {amount_val:,.2f}</b>", ParagraphStyle('Amt', parent=val_style, alignment=2, textColor=colors.HexColor('#059669'), fontSize=11))
        ],
        [
            Paragraph(f"<b>Payment Method:</b> {pay_mode} | <b>Ref / Txn ID:</b> {txn_ref}", subtitle_style),
            Paragraph(f"<b>Total Paid:</b> Rs. {amount_val:,.2f}", ParagraphStyle('Tot', parent=val_style, alignment=2, fontSize=10))
        ]
    ]

    items_table = Table(items_data, colWidths=[84 * mm, 40 * mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E7FF')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 5 * mm))

    # 4. Amenities list banner
    amenities_text = "<font size='7' color='#475569'><b>FACILITIES PROVIDED:</b> Attached Bathrooms in all rooms &bull; High-Speed Wi-Fi &bull; 24/7 CCTV &bull; Washing Machine &bull; Inverter Power Backup</font>"
    story.append(Paragraph(amenities_text, ParagraphStyle('Amen', parent=styles['Normal'], alignment=1)))
    story.append(Spacer(1, 6 * mm))

    # 5. Footer Signatory
    footer_data = [
        [
            Paragraph("<font size='7' color='#94a3b8'>Computer generated official receipt.<br/>Subject to realization of funds.<br/>Thank you for choosing Latha PG!</font>", subtitle_style),
            Paragraph("____________________________<br/><b>Authorized Signatory</b><br/><font size='7.5' color='#64748b'>Latha PG for Gents</font>", ParagraphStyle('Sign', parent=styles['Normal'], alignment=2, fontSize=8, leading=11))
        ]
    ]
    footer_table = Table(footer_data, colWidths=[70 * mm, 54 * mm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(footer_table)

    doc.build(story)
    return buffer.getvalue()
