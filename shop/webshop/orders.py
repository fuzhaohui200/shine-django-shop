from django.contrib.auth import authenticate, login, logout
from django import forms
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.db.models import Sum



from models import *
from cart import *
from forms import *

    
@login_required
def user_orders_view(request):
   return render_to_response("orders.html",{'orders':Order.objects.filter(user=request.user)}, context_instance=RequestContext(request))
   

def order_status_view(request,order_id): 
    order = get_object_or_404(Order,id=order_id)
    amount = order.items.all().aggregate(total=Sum('price'))
    
    if not request.user == order.user:
        return HttpResponse('Youre are not  allowed to do this')    
    return render_to_response("order_status.html",{'order':order,'items':order.items.all(),'total':amount['total'],'checksum':calc_checksum(order.id,amount['total'])}, context_instance=RequestContext(request))
    
