from django.conf.urls.defaults import *
  
urlpatterns = patterns('',
    (r'^products/$', 'api.views.product_list'),
    (r'^products/(\d{1,10})/$', 'api.views.productview'),
)
