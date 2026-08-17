from django.urls import path

from catalog import views

urlpatterns = [
    path("products", views.product_list),
    path("products/<int:product_id>", views.product_detail),
    path("session", views.create_checkout_session),
    path("orders", views.order_list),
    path("orders/<int:order_id>/refund", views.refund_order),
    path("transfers", views.transfers),
    path("webhooks", views.webhooks),
    path("payments", views.payments),
    path("payments/<path:route>", views.payments),
]
