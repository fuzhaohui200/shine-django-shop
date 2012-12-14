"""
Dummy views for the assignment API.
"""
from django.http import HttpResponse

def product_list(request):
    return HttpResponse("api product_list")

def productview(request, product_id):
    return HttpResponse("api product %s"%product_id)