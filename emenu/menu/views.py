from emenu.menu.models import Dish, Menu
from emenu.menu.serializers import DishSerializer, MenuSerializer, MenuDetailSerializer
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework.reverse import reverse


class MenuViewSet(viewsets.ModelViewSet):
    """
    list:
    Get the list of all menus. This is a public method.

    retrieve:
    Get the details of a single menu, including details of dishes. This is a public method.

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
    serializer_class = MenuDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request):
        serializer = MenuSerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)


class DishViewSet(viewsets.ModelViewSet):
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
        'dishes': reverse('dish-list', request=request, format=format),
        'menus': reverse('menu-list', request=request, format=format),
    })
