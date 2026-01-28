from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from main import views
from main.forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('about/', views.about_view, name='about'),
    path('product/<int:pk>/', views.product_detail_view, name='product-detail'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='catalog'), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit-profile'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/update/', views.update_cart, name='update-cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:pk>/', views.order_detail_view, name='order-detail'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/profile/'
    ), name='password_change'),
    path('search/', views.search_view, name='search'),
]
