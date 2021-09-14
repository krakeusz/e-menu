from django.contrib import admin
from emenu.menu.models import Dish, Menu


class DishAdmin(admin.ModelAdmin):
    pass


class MenuAdmin(admin.ModelAdmin):
    pass


admin.site.register(Dish, DishAdmin)
admin.site.register(Menu, MenuAdmin)
