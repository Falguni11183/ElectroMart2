from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('review/', views.review, name='review'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path("logout/", views.logout_page, name="logout"),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path(
    "order-details/<int:id>/",
    views.order_details,
    name="order_details"
),
path("review/<int:id>/", views.review, name="review"),
path("wishlist/", views.wishlist, name="wishlist"),
path("wishlist/add/<int:id>/", views.add_to_wishlist, name="add_to_wishlist"),
path("wishlist/remove/<int:id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
path("profile/", views.profile, name="profile"),
path("dashboard/", views.dashboard, name="dashboard"),
path("admin-products/", views.admin_products, name="admin_products"),
path("add-product/", views.add_product, name="add_product"),
path("edit-product/<int:id>/", views.edit_product, name="edit_product"),
path("delete-product/<int:id>/", views.delete_product, name="delete_product"),
path("admin-orders/", views.admin_orders, name="admin_orders"),
path(
    "update-order-status/<int:id>/",
    views.update_order_status,
    name="update_order_status"
),
path("admin-reviews/", views.admin_reviews, name="admin_reviews"),
path("admin-customers/", views.admin_customers, name="admin_customers"),
path(
    "export-orders/",
    views.export_orders_csv,
    name="export_orders"
),
path('api/products/', views.product_api, name='product_api'),
path("admin-login/", views.admin_login, name="admin_login"),
]