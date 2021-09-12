from emenu.menu.models import Dish, Menu
from emenu.menu.serializers import DishSerializer, MenuSerializer, MenuDetailSerializer
from rest_framework import permissions, viewsets
from rest_framework.response import Response

class MenuViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Menu.objects.all()
    serializer_class = MenuDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request):
        serializer = MenuSerializer(self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

class DishViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated]
