from django.core.exceptions import ValidationError
from django.db.models import Count
from emenu.menu.models import Dish, Menu
from emenu.menu.serializers import DishSerializer, PrivateMenuSerializer, PublicMenuSimpleSerializer, PublicMenuDetailSerializer
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view, schema
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.reverse import reverse
import re


class PublicMenuViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Get the list of all menus. This is a public method.

    retrieve:
    Get the details of a single menu, including details of dishes. This is a public method.
    """
    queryset = Menu.objects.annotate(Count('dishes')).exclude(dishes__count=0)
    serializer_class = PublicMenuDetailSerializer
    permission_classes = [permissions.AllowAny]

    def __process_filter(self, request, field_name):
        """
        Add a GET option to filter results by given field values.
        """
        if field_name in request.query_params:
            filter_by = request.query_params[field_name].split(',')
            for filter_expr in filter_by:
                comparison_op = 'exact'
                match = re.match(r'(gt|gte|lt|lte):(.*)', filter_expr)
                if match:
                    comparison_op = match.group(1)
                    filter_expr = match.group(2)
                kwargs = {f'{field_name}__{comparison_op}': filter_expr}
                try:
                    self.queryset = self.queryset.filter(**kwargs)
                except ValidationError:
                    raise ParseError(
                        detail=f'bad filter expression: {filter_expr}')

    def list(self, request):
        if 'sort_by' in request.query_params:
            sort_by = request.query_params['sort_by'].split(',')
            for sort_expr in sort_by:
                if sort_expr in ['-name', 'name', '-dishes__count', 'dishes__count']:
                    self.queryset = self.queryset.order_by(sort_expr)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=f"unrecognized sort expression: {sort_expr}")
        self.__process_filter(request, 'name')
        self.__process_filter(request, 'date_added')
        self.__process_filter(request, 'date_modified')

        serializer = PublicMenuSimpleSerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)


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
