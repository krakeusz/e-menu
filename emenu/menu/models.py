from django.db import models
from django.db.models import fields


class Dish(models.Model):
    name = fields.CharField(unique=True, max_length=200)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=19, decimal_places=2)
    preparation_time = fields.DurationField()
    date_added = fields.DateTimeField(auto_now_add=True)
    date_modified = fields.DateTimeField(auto_now=True)
    is_vegan = fields.BooleanField(default=False)

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = fields.CharField(unique=True, max_length=100)
    description = fields.TextField()
    date_added = fields.DateTimeField(auto_now_add=True)
    date_modified = fields.DateTimeField(auto_now=True)
    dishes = models.ManyToManyField(to=Dish)

    def __str__(self):
        return self.name
