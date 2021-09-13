from emenu.menu.models import Menu, Dish
from rest_framework import serializers


class DishSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dish
        fields = ['url', 'name', 'description', 'price',
                  'preparation_time', 'date_added', 'date_modified', 'is_vegan']


class PublicMenuDetailSerializer(serializers.HyperlinkedModelSerializer):
    dishes = DishSerializer(many=True)

    class Meta:
        model = Menu
        fields = ['url', 'name', 'description',
                  'date_added', 'date_modified', 'dishes', 'pk']
        extra_kwargs = {
            'url': {
                'view_name': 'public-menu-detail'
            }
        }


class PublicMenuSimpleSerializer(serializers.HyperlinkedModelSerializer):
    dishes = serializers.StringRelatedField(many=True)

    class Meta:
        model = Menu
        fields = ['url', 'name', 'description',
                  'date_added', 'date_modified', 'dishes', 'pk']
        extra_kwargs = {
            'url': {
                'view_name': 'public-menu-detail'
            }
        }


class PrivateMenuSerializer(serializers.HyperlinkedModelSerializer):
    dishes = serializers.HyperlinkedRelatedField(
        many=True, allow_null=True, queryset=Dish.objects.all(), view_name='dish-detail')

    class Meta:
        model = Menu
        fields = ['url', 'name', 'description',
                  'date_added', 'date_modified', 'dishes', 'pk']
        extra_kwargs = {
            'url': {
                'view_name': 'private-menu-detail'
            }
        }
