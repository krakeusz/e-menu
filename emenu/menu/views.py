from django.core.exceptions import ValidationError
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from emenu.menu.filters import MenuFilter
from emenu.menu.models import Dish, Menu
from emenu.menu.serializers import DishSerializer, PrivateMenuSerializer, PublicMenuSimpleSerializer, PublicMenuDetailSerializer
from rest_framework import permissions, viewsets, filters, mixins
from rest_framework.decorators import api_view, schema
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.reverse import reverse
import re


class PublicMenuViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin):
    """
    Get the list of all menus. This is a public method.

    The optional 'ordering' parameter accepts ordering by two fields:
    - dishes__count
    - name

    By default, the results are sorted in ascending order. To sort in descending order, add '-' prefix. For example,

    <pre>?ordering=-dishes__count,name</pre>

    The rest of the optional parameters allow filtering the results. For example,

    <pre>?date_added__lt=2021-01-01</pre>

    will show only the menus added before year 2021.
    """
    queryset = Menu.objects.annotate(Count('dishes')).exclude(dishes__count=0)
    serializer_class = PublicMenuSimpleSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = MenuFilter
    ordering_fields = ['name', 'dishes__count']


class PublicMenuDetailsViewSet(viewsets.GenericViewSet,
                               mixins.RetrieveModelMixin):
    """
    Get the details of a single menu, including details of dishes. This is a public method.
    """
    queryset = Menu.objects.all()
    serializer_class = PublicMenuDetailSerializer
    permission_classes = [permissions.AllowAny]


class PrivateMenuViewSet(viewsets.ModelViewSet):
    """
    list:
    Get the list of all menus. This method requires the user to be logged in.

    retrieve:
    Get the details of a single menu, including details of dishes. This method requires the user to be logged in.

    create:
    Add a new menu. This method requires the user to be logged in.

    update:
    Modify a menu. This method requires the user to be logged in.

    partial_update:
    Modify a menu. This method requires the user to be logged in.

    destroy:
    Delete a menu. This method requires the user to be logged in.
    """
    queryset = Menu.objects.all()
    serializer_class = PrivateMenuSerializer
    permission_classes = [permissions.IsAuthenticated]


class PrivateDishViewSet(viewsets.ModelViewSet):
    """
    list:
    Get the list of all dishes. This method requires the user to be logged in.

    retrieve:
    Get the details of a single dish. This method requires the user to be logged in.

    create:
    Add a new dish. This method requires the user to be logged in.

    update:
    Modify a dish. This method requires the user to be logged in.

    partial_update:
    Modify a dish. This method requires the user to be logged in.

    destroy:
    Delete a dish. This method requires the user to be logged in.
    """
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@schema(None)
def api_root(request, format=None):
    """
    This is an API that allows fetching and modifying a restaurant menu.

    To modify the menus, you need to be logged in.

    For more, see the [documentation section](docs/).
    """
    return Response({
        'docs': reverse('swagger-ui', request=request, format=format),
        'private-dishes': reverse('dish-list', request=request, format=format),
        'private-menus': reverse('private-menu-list', request=request, format=format),
        'public-menus': reverse('public-menu-list', request=request, format=format),
    })
