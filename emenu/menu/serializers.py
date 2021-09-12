from emenu.menu.models import Menu, Dish
from rest_framework import serializers

class MenuSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Menu
        fields = ['url', 'name', 'description', 'date_added', 'date_modified', 'dishes']

class DishSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dish
        fields = ['url', 'name', 'description', 'price', 'preparation_time', 'date_added', 'date_modified', 'is_vegan']