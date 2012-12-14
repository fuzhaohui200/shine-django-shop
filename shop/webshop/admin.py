from django.contrib import admin
from webshop.models import *



admin.site.register(Category)
class UploadInline(admin.StackedInline):
    model = Upload
    extra = 0
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'quantity', 'available','currentPrice','category')
    list_filter = ['quantity', 'available', 'currentPrice', 'category']
    list_display_links = ['id','title']
    search_fields = ['title']
    inlines = [UploadInline]
    
admin.site.register(Product, ProductAdmin)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','user','product','hidden','time','parent','content')
    list_filter = ['user', 'hidden', 'product', 'parent','time']
    search_fields = ['product','user']
    readonly_fields = ['user','product','time','parent','content']
    date_hierarchy = 'time'

admin.site.register(Comment,CommentAdmin)
class RatingAdmin(admin.ModelAdmin):
    readonly_fields = ['product','user','rating','time']
    date_hierarchy = 'time'
admin.site.register(Rating,RatingAdmin)
admin.site.register(UserProfile)
admin.site.register(WebPage)
admin.site.register(MusicLabel)
class SaleItemsInline(admin.StackedInline):
    model = SaleItem
    readonly_fields = ['price','product']
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'shippingDate', 'orderDate','completed')
    list_display_links = ['id']
    readonly_fields = ['user','completed','ref','orderDate','deliverAddress']
    list_filter = ['orderDate', 'completed',]
    date_hierarchy = 'orderDate'

    fieldsets = [
        (None,               {'fields': ['user']}),
        ('Shipping', {'fields': ['deliverAddress','shippingDate']}),
        ('Order Status', {'fields': ['completed','ref']}),
    ]
    inlines = [SaleItemsInline]


admin.site.register(Order,OrderAdmin)
class UploadAdmin(admin.ModelAdmin):
    list_display = ('id','product', 'created','uploaded_file','mimetype')
    list_display_links = ['id','product']
    readonly_fields = ['mimetype','product','created']
    date_hierarchy = 'created'
admin.site.register(Upload,UploadAdmin)
