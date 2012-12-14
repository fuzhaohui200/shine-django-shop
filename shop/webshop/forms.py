from django.forms import ModelForm
from django import forms
from webshop.models import SaleItem, Comment, Order, Upload

#coihes for rating
RATING_CHOICES = (
    ('1', 1),
    ('2', 2),
    ('3', 3),
    ('4', 4),
    ('5', 5),
)

#This is for Ex3.4
class SaleItemForm(ModelForm):
  class Meta:
    model = SaleItem
	
class CommentForm(forms.Form):
        comment = forms.CharField(widget=forms.Textarea)
        parent = forms.IntegerField(widget=forms.HiddenInput())

    
class RatingForm(forms.Form):
	rating = forms.ChoiceField(choices=RATING_CHOICES,widget=forms.RadioSelect)

class OrderForm(forms.Form):
    deliverAddress = forms.CharField(widget=forms.Textarea)
    #shippingDate = forms.DateField(widget=forms.DateInput())
class UploadForm(ModelForm):
  class Meta:
    model = Upload
