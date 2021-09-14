"""emenu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from emenu.menu import views
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework.schemas import get_schema_view

public_router = SimpleRouter()
public_router.register(r'menu', views.PublicMenuViewSet,
                       basename='public-menu')
public_router.register(r'menu', views.PublicMenuDetailsViewSet,
                       basename='public-menu')

private_router = SimpleRouter()
private_router.register(
    r'menu', views.PrivateMenuViewSet, basename='private-menu')
private_router.register(
    r'dishes', views.PrivateDishViewSet)

urlpatterns = [
    path('', views.api_root, name='root'),
    path('private/', include(private_router.urls)),
    path('public/', include(public_router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('openapi/', get_schema_view(
        title="eMenu API",
        description="API for fetching and managing restaurant menu",
        version="1.0.0",
        public=True,
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='menu/swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]
