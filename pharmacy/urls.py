from django.urls import path
from .views import CreateListPharmacyCategory, DetailPharmacyCategory

app_name = 'pharmacy'

urlpatterns =[
    path("categories/", view=CreateListPharmacyCategory.as_view(), name="create_pharmacy_category"),
    path("categories/<int:id>/", view=DetailPharmacyCategory.as_view(), name="detail_pharmacy_category"),
]