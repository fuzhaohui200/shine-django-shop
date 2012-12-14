from django.conf.urls.defaults import *
from django.conf import settings

# if you add new views, don't forget the imports!
from webshop.accounts import *
from webshop.cart import *
from webshop.orders import *
from django.contrib.auth.views import login, logout
from webshop.models import Product
from django.views.generic import list_detail
from django.contrib import admin
admin.autodiscover()

 
urlpatterns = patterns('', #This empty string is view prefix, don't touch unless you know what you're doing 
        (u'^$', frontpage),
        (u'^about/$', about),
        (u'^products/(\d{1,10})/$', productview),
        (u'^aproducts/$', available_products),
        (u'^addsaleitem/$', add_saleitem),
        (u'^products/$', product_list),
        (u'^api/', include('api.urls')),
        (u'^cart/$', cart_view),
        (u'^cart/checkout/$', checkout_view),
        (u'^cart/confirm/$', confirm),
        (u'^cart/payment/success$', payment_success),
        (u'^cart/payment/cancel$', payment_cancel),
        (u'^accounts/login/$', login_view),
        (u'^accounts/logout/$', logout_view),
        (u'^accounts/register/$', register_view),
        (u'^accounts/my/$', account_view),
        (u'^admin/report/$', 'webshop.admin_views.report'),
		(u'^admin/', include(admin.site.urls)),
        (u'^comment/(\d{1,10})/$', comment),
        (u'^comment/(\d{1,10})/(\d{1,10})/$', comment),
        (u'^rate/(\d{1,10})/$', rate),
        (u'^orders/$', user_orders_view),
        (u'^orders/(\d{1,10})/$', order_status_view),
        (u'^search/$', search),


)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT }),
    )
