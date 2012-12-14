from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from decimal import Decimal

from models import *
from forms import *
import json
import md5
from django.db.models import Sum

def calc_checksum(pid, amount):
    #for making a payment
    sid = "NAJMusicWebShop"
    key = "e62c2691f36cb9254094491cd10619da"
    checksum_str = "pid=%s&sid=%s&amount=%s&token=%s"%(pid, sid, amount, key) 
    #print checksum_str
    m = md5.new(checksum_str)
    checksum = m.hexdigest()
    return checksum

def confirm_checksum(pid, ref, checksum):
    #check checksum
    pid = pid
    ref = ref
    key = "e62c2691f36cb9254094491cd10619da"
    checksum_str = "pid=%s&ref=%s&token=%s"%(pid, ref, key)
    m = md5.new(checksum_str)
    checksum_new = m.hexdigest()
    if checksum == checksum_new:
        return True
    else:
        return False

def new_checksum(pid, ref):
    #new checksum for response
    pid = pid
    ref = ref
    key = "e62c2691f36cb9254094491cd10619da"
    checksum_str = "pid=%s&ref=%s&token=%s"%(pid, ref, key)
    m = md5.new(checksum_str)
    checksum = m.hexdigest()
    return checksum


def deserialize_cart(request):
    """
    Deserialize JSON object into a dictionary
    """
    cart = {}
    
    if request.COOKIES.has_key('cart'):
        # deserialize cart from json object
        cartstr = request.COOKIES['cart']
        cart = json.loads(cartstr)

    return cart

def get_cart_product_list(cart):
    """
    Converts cart dictionary into a list of products (with .amount).
    Total amount of items in the cart and total price is also returned.

    Silently ignores non-existent product ids.
    """
    productsInCart = []
    totalAmount = 0
    totalPrice = Decimal(0)

    for key in cart:
        try:
            p = Product.objects.get(id=key)
        except Product.DoesNotExist:
            p = None

        if p != None:
            p.amount = cart[key]
            totalAmount += p.amount
            totalPrice += p.currentPrice * p.amount
            productsInCart.append(p)

    return (productsInCart, totalAmount, totalPrice)

def cart_context_processor(request):
    cart = deserialize_cart(request)
    productsInCart, totalAmount, totalPrice = get_cart_product_list(cart)

    d = {}
    if len(productsInCart) > 0:
        d['productsInCart_context'] = productsInCart
    d['productsInCartNum_context'] = totalAmount

    return d
    

def cart_view(request):
    t = get_template('cart.html')
    context = RequestContext(request)
    resp = HttpResponse()
    cart = deserialize_cart(request)

    try:
        if request.REQUEST["add"]:

            # x validate that add value is a number
            # x validate that it corresponds a product that is available
            # - parse client cookie (if available)
            # - add product to the client cookie
            # - send back the cookie to the client

            # find the product to be added 
            product = get_object_or_404(Product, id=request.REQUEST["add"]) 
            prodidstr = "%s" % product.id

            if cart.has_key(prodidstr):
                cart
                cart[prodidstr] = int(cart[prodidstr]) + 1
            else:
                cart[prodidstr] = 1


            # render the page
            context['product'] = product

            cartstr = json.dumps(cart)
            resp.set_cookie('cart', cartstr)

    except (KeyError):
        pass
    
    try:
        if request.REQUEST["remove"]:

            product = get_object_or_404(Product, id=request.REQUEST["remove"]) 
            prodidstr = "%s" % product.id
            # remove product from cart either completely or reduce the amount
            if cart.has_key(prodidstr):
                if cart[prodidstr] == 1 or cart[prodidstr] == 0:
                    del cart[prodidstr]
                else : 
                    cart[prodidstr] = int(cart[prodidstr]) - 1


            # render the page
            #context['product'] = product

            cartstr = json.dumps(cart)
            resp.set_cookie('cart', cartstr)
    except (KeyError):
        pass
    
    try:
        if request.REQUEST["empty"]:
            cart = []
            resp.delete_cookie('cart')
    except (KeyError):
        pass
    # populate a product list for printing the cart contents
    productsInCart = []
    totalAmount = 0
    for key in cart:
        try:
            p = Product.objects.get(id=key)
        except Product.DoesNotExist:
            p = None

        if p != None:
            p.amount = cart[key]
            totalAmount = totalAmount + int(cart[key])
            productsInCart.append(p)

    context['productsInCart'] = productsInCart
    context['productsInCartNum'] = "%s" % totalAmount
    resp.set_cookie('totalAmount', totalAmount)
    html = t.render(context)    
    resp.content = html
    return resp


    
@login_required
def checkout_view(request):
    t = get_template('checkout.html')
    context = RequestContext(request)
    resp = HttpResponse()
   
    cart = deserialize_cart(request)
    productsInCart, totalAmount, totalPrice = get_cart_product_list(cart)
    
    context['productsInCart'] = productsInCart
    context['total'] = totalPrice
   
    # get user address from the profile
    try:
        up = UserProfile.objects.get(user=request.user)
        address = up.homeAddress
    except UserProfile.DoesNotExist:
        address = ""


    #new order form
    form = OrderForm(data={'deliverAddress' : address})
    context['form'] = form
    
    html = t.render(context)    
    resp.content = html
    return resp
    
@login_required
def confirm(request):
    t = get_template('checkout.html')
    context = RequestContext(request)
    resp = HttpResponse()
    
    cart = deserialize_cart(request)
    productsInCart, totalAmount, totalPrice = get_cart_product_list(cart)
    form = OrderForm(request.POST)
    
    if form.is_valid():
        
        #Create a new order
        order = Order()
        order.user = request.user
        #order.shippingDate = form.cleaned_data['shippingDate']
        order.deliverAddress = form.cleaned_data['deliverAddress']
        order.completed = False
        if cart:
            order.save() # dont save empty orders
        
        for p in productsInCart:
            for i in range(0, p.amount):
                s = SaleItem(product=p,price=p.currentPrice,order=order,shipped=False)
                s.sell()
                s.save()
            
        #delete cookie 
        resp.delete_cookie('cart')
        # render new temp
        t = get_template('payment.html')
        context['order'] = order
        context['total'] = totalPrice
        context['checksum'] = calc_checksum(order.id,totalPrice)
        html = t.render(context)    
        resp.content = html
        return resp
       
    else: 
        #form not valid
        context['form'] = form
    
    context['productsInCart'] = productsInCart
    context['total'] = totalPrice
               
    html = t.render(context)    
    resp.content = html
        
    return resp
    
def payment_success(request):
    if request.method == "GET":
        pid = request.GET['pid']
        ref = request.GET['ref']
        checksum = request.GET['checksum']
        if confirm_checksum(pid,ref,checksum):
            order = Order.objects.get(id=pid)
            order.ref = ref
            order.save()
            return render_to_response("payment.html",{'success':True, 'ref':ref, 'order_ref':order.ref},context_instance=RequestContext(request))        
    return render_to_response("payment.html",{'error':True, 'pid':pid,'ref':ref,'checksum':checksum,'checksum_new':new_checksum(pid,ref)},context_instance=RequestContext(request))        
            
        
        
def payment_cancel(request):
    if request.method == "GET":
        pid = request.GET['pid']
        ref = request.GET['ref']
        checksum = request.GET['checksum']
        if confirm_checksum(pid,ref,checksum):
            order = Order.objects.get(id=pid)
            amount = order.items.all().aggregate(total=Sum('price'))
            return render_to_response("payment.html",{'cancel':True,'order':order,'total':amount['total'],'checksum':calc_checksum(order.id,amount['total'])},context_instance=RequestContext(request))
    return render_to_response("payment.html",{'error':True, 'pid':pid,'ref':ref,'checksum':checksum,'checksum_new':new_checksum(pid,ref)},context_instance=RequestContext(request))    
