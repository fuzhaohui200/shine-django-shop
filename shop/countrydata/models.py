from django.db import models

class Continent(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=2, unique=True)
    class Meta:
        ordering = ['name']
    pass

class Country(models.Model):
    name = models.CharField(max_length=50)
    capital = models.CharField(max_length=50)
    code = models.CharField(max_length=50, unique=True)
    population = models.PositiveIntegerField()
    area = models.PositiveIntegerField()
    continent = models.ForeignKey('Continent')
    class Meta:
        ordering = ['name']
    pass