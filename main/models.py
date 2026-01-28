from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=10, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CustomUser'
        indexes = [
            models.Index(fields=['username'], name='idx_user_username'),
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['phone'], name='idx_user_phone'),
        ]

    def __str__(self):
        return self.username
    
class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    open_hours = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_store_name'),
        ]

    def __str__(self):
        return self.name
    
class OrderStatus(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_orderstatus_name'),
        ]

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    status = models.ForeignKey('OrderStatus', on_delete=models.SET_NULL, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)
    store = models.ForeignKey('Store', on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['order_date'], name='idx_order_date'),
            models.Index(fields=['user'], name='idx_order_user'),
            models.Index(fields=['store'], name='idx_order_store'),
            models.Index(fields=['order_date','status'], name='idx_order_date_status'),
            models.Index(fields=['user','status'], name='idx_order_user_status')
        ]

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['order','product'], name='idx_orderitem_order_product'),
        ]

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    photo = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_brand_name')
        ]

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    photo = models.CharField(max_length=255, blank=True)
    certificate = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['category'], name='idx_product_category'),
            models.Index(fields=['brand'], name='idx_product_brand'),
            models.Index(fields=['name'], name='idx_product_name'),
            models.Index(fields=['name', 'category'], name='idx_product_name_category'),
        ]

    def __str__(self):
        return self.name

class StoreInventory(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    updated_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['store'], name='idx_storeinventory_store'),
            models.Index(fields=['product'], name='idx_storeinventory_product'),
            models.Index(fields=['store', 'product'], name='idx_storeinv_store_product'),
        ]

class Wishlist(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f"Wishlist #{self.id} for {self.user.username}"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey('Wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['wishlist'], name='idx_wishlistitem_wishlist'),
            models.Index(fields=['product'], name='idx_wishlistitem_product'),
        ]

class ReviewLog(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    grade = models.IntegerField()
    comment = models.TextField(blank=True)
    review_date = models.DateTimeField(auto_now_add=True)
    viewable = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_reviewlog_user'),
            models.Index(fields=['product'], name='idx_reviewlog_product'),
            models.Index(fields=['user', 'product'], name='idx_reviewlog_user_product'),
        ]

class Nutrient(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='idx_nutrient_name')
        ]

    def __str__(self):
        return self.name

class ProductComposition(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    nutrient = models.ForeignKey('Nutrient', on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.nutrient.name} in {self.product.name}: {self.amount} г"
