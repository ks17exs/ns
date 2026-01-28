from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(CustomUser, UserAdmin)

models_to_register = [
    Store, OrderStatus, Order, OrderItem,
    ProductCategory, Brand, Country, Product,
    StoreInventory, Wishlist, WishlistItem,
    ReviewLog, ProductComposition, Nutrient
]

for model in models_to_register:
    admin.site.register(model)