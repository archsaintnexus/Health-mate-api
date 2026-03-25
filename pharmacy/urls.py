from django.urls import path
from .views import (CreateListPharmacyCategory, DetailPharmacyCategory,
                    CreateListPharmacyProduct, DetailPharmacyProduct, PharmacyCatalogView, PharmacyOrderCreateView)

app_name = 'pharmacy'

urlpatterns =[
    path("categories/", view=CreateListPharmacyCategory.as_view(), name="create_pharmacy_category"),
    path("categories/<int:pk>/", view=DetailPharmacyCategory.as_view(), name="detail_pharmacy_category"),

    path("products/", view=CreateListPharmacyProduct.as_view(), name="create_pharmacy_product"),
    path("products/<int:pk>/", view=DetailPharmacyProduct.as_view(), name="detail_pharmacy_product"),

    path("catalog/", PharmacyCatalogView.as_view(), name="pharmacy-catalog"),
    path("orders/", PharmacyOrderCreateView.as_view(), name="pharmacy-order-create"),
]