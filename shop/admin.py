from django.contrib import admin
from .models import *


class GameAdmin(admin.ModelAdmin):
    list_display = ['title']


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['ref', 'amount']


class ItemAdmin(admin.ModelAdmin):
    list_display = ['game', 'version']
    fields = ['game', 'version', 'price']


class CartAdmin(admin.ModelAdmin):
    list_display = ['user_token']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['status', 'total']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cart']


def upload(self, request, queryset):
    for item in queryset:
        item.add_to_db()
upload.short_description = 'Add new items to database'


class NewItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'added']
    actions = [upload]


admin.site.register(Game, GameAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(NewItem, NewItemAdmin)
admin.site.register(Profile, ProfileAdmin)
