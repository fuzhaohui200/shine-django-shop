from webshop.models import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count,Avg
from django.contrib.auth.models import User


def report(request):
    commented = Comment.objects.values('product__title').annotate(count=Count('product__title')).order_by('count').reverse()[:10]
    items = SaleItem.objects.values('product__title').annotate(count=Count('product__title')).order_by('count').reverse()[:10]
    rated = Rating.objects.values('product__title').annotate(rate=Avg('rating')).order_by('rate').reverse()[:10]
    user_comments = Comment.objects.values('user__username').annotate(count=Count('user__username')).order_by('count').reverse()

    return render_to_response(
        "admin/webshop/report.html",
        {'saleitems_list' : items,'rated_list':rated,'commented_list':commented,'users_list':user_comments},
        RequestContext(request, {}),
    )
report = staff_member_required(report)
