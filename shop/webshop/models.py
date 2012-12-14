from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.title

class MusicLabel(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey('Category', related_name='products')
    musiclabel = models.ForeignKey('MusicLabel', related_name='products', blank=True, null=True)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    # URLField doesn't allow relative URLs :(
    imageUrl = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.BigIntegerField(default=0)
    available = models.BooleanField()
    currentPrice = models.DecimalField(max_digits=7, decimal_places=2)
    def decrease_quantity(self):
        self.quantity -= 1
        self.save()

    def __unicode__(self):
        return self.title

class SaleItem(models.Model):
    price = models.DecimalField(max_digits=7, decimal_places=2)
    product = models.ForeignKey('Product', related_name='saleitems')
    order =  models.ForeignKey('Order', related_name='items')
    shipped = models.BooleanField()
    
    def sell(self):
        self.product.decrease_quantity()
    
    def __unicode__(self):
        return  u'%s %s' % (self.price, self.product.title)
    def save(self,*args, **kwargs):
        super(SaleItem, self).save(*args, **kwargs) # Call the "real" save() method.
        self.order.check_completed()

class WebPage(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data = models.TextField()
    modifiedDate = models.DateField(auto_now=True)

    def __unicode__(self):
        return self.name

class Comment(models.Model):
    product = models.ForeignKey('Product', related_name='comments')
    parent = models.ForeignKey('Comment', related_name='childComments',blank=True,null=True)
    user = models.ForeignKey(User, related_name='comments')
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    hidden = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.product.title + ' by ' + self.user.username
    
    def get_children(self):
        return self._default_manager.filter(parent=self)

    def get_descendants(self):
        descs = set(self.get_children())
        for node in list(descs):
            descs.update(node.get_descendants())
        return descs
    def delete(self):
        self.hidden=True
        self.save()
    
class Rating(models.Model):
    product = models.ForeignKey('Product', related_name='ratings')
    user = models.ForeignKey(User, related_name='ratings')
    rating = models.PositiveSmallIntegerField()
    time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.product.title + " " + self.user.username
    
 
class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders')
    orderDate = models.DateField(auto_now_add=True)
    shippingDate = models.DateField(null=True)
    deliverAddress = models.TextField()
    completed = models.BooleanField()
    ref = models.IntegerField(null=True)
    class Meta:
        permissions = (
            ("can_view_status", "Can check order status"),
        )

    def check_completed(self):
        if not self.items.exclude(shipped=True).exists() and self.ref:
            self.completed = True
        else:
            self.completed = False
        self.save()    
     
    
    def __unicode__(self):
        return  u'%s %s' % (self.user.username, self.orderDate)

class UserProfile(models.Model):
    homeAddress = models.TextField(blank=True, null=True)
    phoneNumber = models.CharField(max_length=255,blank=True,null=True)
    user = models.ForeignKey(User, unique=True)
   
class Upload(models.Model): 
    uploaded_file = models.FileField(upload_to='uploads')
    mimetype = models.CharField(max_length=64, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    product = models.ForeignKey('Product', related_name='uploads')
    def save(self,*args, **kwargs):
        super(Upload, self).save(*args, **kwargs) # Call the "real" save() method.

        p = self.product
        p.imageUrl = self.uploaded_file.url # change products imageUrl to uplaoded_files url
        p.save()
    def __unicode__(self):
        return  u'%s' % (self.uploaded_file.name)
        
        

