from weasyprint import Html
from django.shortcuts import render
html=Html(string=render(request, 'invoice/pdf/invoice.html', context).content)