import django_filters
from emenu.menu.models import Menu


class MenuFilter(django_filters.FilterSet):
    class Meta:
        model = Menu
        fields = {
            'name': ['exact'],
            'date_added': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'date_modified': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
