from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

try:
    from django.utils import importlib
except ImportError:
    import importlib

from pis_sales.models import SalesHistory

# -*- coding: UTF-8 -*-
from os import path
from django.conf import settings
from django.http import HttpResponse

INV_MODULE = 'invoice.pdf'
INV_LOGO =  'media/retailer/logo/logo.png'
INV_CURRENCY = 'Dh'
INV_CURRENCY_SYMBOL = '-'
# INV_EMAIL_SUBJECT = getattr(settings, 'INV_EMAIL_SUBJECT', u'[%s] Invoice %%(invoice_id)s' % (SITE_NAME))





def format_currency(amount, currency):
    if currency:
        return u"{1.pre_symbol} {0:.2f} {1.post_symbol} {1}".format(amount, currency)

    return u"%s %.2f %s" % (
        INV_CURRENCY_SYMBOL, amount, INV_CURRENCY
    )


def pdf_response(draw_funk, file_name, *args, **kwargs):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=\"%s\"" % file_name
    draw_funk(response, *args, **kwargs)
    return response


# def send_invoices():
#     from ..models import Invoice

#     for invoice in Invoice.objects.get_due():
#         invoice.send_email()

def draw_header(canvas):
    """ Draws the invoice header """
    canvas.setStrokeColorRGB(0.9, 0.5, 0.2)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)
    canvas.setFont('Helvetica', 16)
    canvas.drawString(18 * cm, -1 * cm, 'Invoice')
    canvas.drawInlineImage(INV_LOGO, 1 * cm, -1 * cm, 250, 16)
    canvas.setLineWidth(4)
    canvas.line(0, -1.25 * cm, 21.7 * cm, -1.25 * cm)


def draw_address(canvas):
    """ Draws the business address """
    business_details = (
        u'COMPANY NAME LTD',
        u'STREET',
        u'TOWN',
        U'COUNTY',
        U'POSTCODE',
        U'COUNTRY',
        u'',
        u'',
        u'Phone: +00 (0) 000 000 000',
        u'Email: example@example.com',
        u'Website: www.example.com',
        u'Reg No: 00000000'
    )
    canvas.setFont('Helvetica', 9)
    textobject = canvas.beginText(13 * cm, -2.5 * cm)
    for line in business_details:
        textobject.textLine(line)
    canvas.drawText(textobject)


def draw_footer(canvas):
    """ Draws the invoice footer """
    note = (
        u'Bank Details: Street address, Town, County, POSTCODE',
        u'Sort Code: 00-00-00 Account No: 00000000 (Quote invoice number).',
        u'Please pay via bank transfer or cheque. All payments should be made in CURRENCY.',
        u'Make cheques payable to Company Name Ltd.',
    )
    textobject = canvas.beginText(1 * cm, -27 * cm)
    for line in note:
        textobject.textLine(line)
    canvas.drawText(textobject)


# inv_module = importlib.import_module('invoice.pdf')
# header_func = inv_module.draw_header
# address_func = inv_module.draw_address
# footer_func = inv_module.draw_footer

buffer=StringIO()
def draw_pdf(buffer, invoice):
    """ Draws the invoice """
    canvas = Canvas(buffer, pagesize=A4)
    canvas.translate(0, 29.7 * cm)
    canvas.setFont('Helvetica', 10)

    canvas.saveState()
    draw_header(canvas)
    canvas.restoreState()

    canvas.saveState()
    draw_footer(canvas)
    canvas.restoreState()

    canvas.saveState()
    draw_address(canvas)
    canvas.restoreState()

    # Client address
    textobject = canvas.beginText(1.5 * cm, -2.5 * cm)
    if invoice.address.contact_name:
        textobject.textLine(invoice.address.contact_name)
    textobject.textLine(invoice.address.address_one)
    if invoice.address.address_two:
        textobject.textLine(invoice.address.address_two)
    textobject.textLine(invoice.address.town)
    if invoice.address.county:
        textobject.textLine(invoice.address.county)
    textobject.textLine(invoice.address.postcode)
    textobject.textLine(invoice.address.country.name)
    canvas.drawText(textobject)

    # Info
    textobject = canvas.beginText(1.5 * cm, -6.75 * cm)
    textobject.textLine(u'Invoice ID: %s' % invoice.invoice_id)
    textobject.textLine(u'Invoice Date: %s' % invoice.invoice_date.strftime('%d %b %Y'))
    textobject.textLine(u'Client: %s' % invoice.user.username)
    canvas.drawText(textobject)

    # Items
    data = [[u'Quantity', u'Description', u'Amount', u'Total'], ]
    for item in invoice.items.all():
        data.append([
            item.quantity,
            item.description,
            format_currency(item.unit_price, invoice.currency),
            format_currency(item.total(), invoice.currency)
        ])
    data.append([u'', u'', u'Total:', format_currency(invoice.total(), invoice.currency)])
    table = Table(data, colWidths=[2 * cm, 11 * cm, 3 * cm, 3 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
        ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
    ])
    tw, th, = table.wrapOn(canvas, 15 * cm, 19 * cm)
    table.drawOn(canvas, 1 * cm, -8 * cm - th)

    canvas.showPage()
    canvas.save()

invoice = SalesHistory.objects.get(42)

draw_pdf()