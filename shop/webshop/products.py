from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.db.models import Avg, Max, Min

from models import *
from forms import *

from django.template import Template

def frontpage(request):
    s = WebPage.objects.get(name="frontpage").data
    tpl = Template(s)

    return HttpResponse(tpl.render(RequestContext(request)))

def about(request):
    return HttpResponse("about page")

def addToThreaded(clist, c, level=0):
    clist.append(c)
    c.level = (1,)*level
    for cc in c.childComments.all():
        addToThreaded(clist, cc, level+1)

def product_list(request):
    products = []
    label = None
    max = request.GET.get('max', None) #get max or None
    min = request.GET.get('min', None) #get min or None
            
    cat = []
    for category in Category.objects.all():

        if request.GET.has_key('label'):
            try:
                label = request.GET['label']
                musiclabel = MusicLabel.objects.get(name=label)
                products = Product.objects.filter(available=True, musiclabel=musiclabel, category=category)
                if max is not None and min is not None:
                   products = products.filter(currentPrice__gte=min).filter(currentPrice__lte=max) # limit query if GET max and min is set
            except MusicLabel.DoesNotExist:
                pass

        else:
            products = Product.objects.filter(available=True, category=category)
            if max is not None and min is not None:
                products = products.filter(currentPrice__lte=max).filter(currentPrice__gte=min) # limit query if GET max and min is set

        if len(products) > 0:
            category.prods = products
            cat.append(category)
            
   
    range = products.aggregate(max=Max('currentPrice'), min=Min('currentPrice')) #price range

    return render_to_response(
        "product_list.html",
        {   
            "categories" : cat,
            "label" : label,
            "range":range

        },
        context_instance=RequestContext(request))

def productview(request, product_id):
    comments = Comment.objects.filter(product=product_id)
    # latest uploaded file and the host
    try:
        upload = Upload.objects.filter(product=product_id).latest('created')
    except Upload.DoesNotExist:
        upload = None 
    host = request.get_host()    
    # construct a comment root list (comments without a parent comment)
    rlist = []
    for c in comments:
        if c.parent == None:
            rlist.append(c)
    
    # using the root list, construct a "threaded" list using a DFS
    clist = []
    for c in rlist:
        addToThreaded(clist, c)

    bought = False
    if request.user.is_authenticated():
        if len(SaleItem.objects.filter(order__user=request.user, product__id=product_id)) > 0:
            bought = True

    ratings = Rating.objects.filter(product__exact=product_id)
    votes = ratings.count()
    try:
        voted = Rating.objects.get(product=product_id,user=request.user.id)
        voted=True
    except Rating.DoesNotExist:
        voted = False
    rate = ratings.aggregate(rating=Avg('rating'))

    return render_to_response(
        "product_view.html",
        {'product' : get_object_or_404(Product, id=product_id), 
         'ratingForm':RatingForm(), 
         'comments':clist, 
         'votes':votes, 
         'rate':rate, 
         'voted':voted,
         'bought':bought,
         'upload':upload,
         'host':host
         },
         context_instance=RequestContext(request))

def available_products(request):
    return render_to_response("product_list.html", {"products" :
    Product.objects.filter(quantity__gt=0)})

def add_saleitem(request):
    if request.method == 'POST':
        form = SaleItemForm(request.POST)

        if form.is_valid():
            p = form.save()
            return HttpResponseRedirect("/products/%d/" % (p.id))

    else:
        # GET, empty form
        form = SaleItemForm()


    return render_to_response("add_saleitem.html", {"form" : form})

def comment(request,product_id, parent_id=None):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        # GET form
        form = CommentForm(request.POST)     
        if form.is_valid():
            #Validated form
            content = form.cleaned_data['comment']
            user = request.user
            parent_id = form.cleaned_data['parent']
            #If parent id set (!=0)
            if parent_id is not 0:
                parent = get_object_or_404(Comment, id=parent_id)
                c=Comment(user=user,content=content, product=product, parent=parent)
            else:             
                c=Comment(user=user,content=content, product=product)
            c.save()
            return HttpResponseRedirect("/products/%d/" % (product.id))

    elif request.method == 'GET':
        if 'delete' in request.GET and request.GET['delete'] and request.user.is_staff:
            id = request.GET['delete']
            c = get_object_or_404(Comment,id=id)
            c.delete()
            return redirect(productview,(product_id))

    # empty form
    form = CommentForm()

    return render_to_response("add_comment.html", {"form" : form, "product_id":product_id, "parent_id":parent_id})


def rate(request, product_id):
    try:
        voted = Rating.objects.get(product=product_id,user=request.user.id)
        voted=True
    except Rating.DoesNotExist:
        voted = False

    if request.method == 'POST':
        form = RatingForm(request.POST)     
        if form.is_valid() and not voted:
            rating = form.cleaned_data['rating']
            user = request.user
            product = get_object_or_404(Product, id=product_id)
            r=Rating(user=user,rating=rating, product=product)
            r.save()
            return HttpResponseRedirect("/products/%d/" % (product.id))

    # return back to product
    return render_to_response("product_view.html",{'product' :
        get_object_or_404(Product, id=product_id), 'ratingForm':RatingForm(), 'comments':comments, 'voted':voted},context_instance=RequestContext(request))

def search(request):
    """
    Searching function, searches product titles. Advice from djangobook.com
    """
    errors = []
    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            errors.append('Enter a search term.')
        elif len(q) > 20:
            errors.append('Please enter at most 20 characters.')
        else:
            products = Product.objects.filter(available=True).filter(title__icontains=q)
            if request.is_ajax():
                return render_to_response('search_results_ajax.html',
                {'products': products, 'query': q,})
            else:
                return render_to_response('search_results.html',
                {'products': products, 'query': q,})
    return render_to_response('search_form.html',
        {'errors': errors})
