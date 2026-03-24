from django.shortcuts import render
from rest_framework.generics import CreateAPIView,ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework import permissions


from .models import PharmacyCategory, PharmacyProduct
from .serializers import PharmacyCategorySerializer, PharmacyProductSerializer
# Create your views here.

## Create CRUD for catagories
class CreateListPharmacyCategory(ListCreateAPIView):
    queryset = PharmacyCategory.objects.all()
    serializer_class = PharmacyCategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return []

class DetailPharmacyCategory(RetrieveUpdateDestroyAPIView):
    queryset = PharmacyCategory.objects.all()
    serializer_class = PharmacyCategorySerializer
    permission_classes = [permissions.IsAdminUser]


## Create CRUD for  products
class CreateListPharmacyProduct(ListCreateAPIView):
    queryset = PharmacyProduct.objects.all()
    serializer_class = PharmacyProductSerializer
    permission_classes = [permissions.IsAdminUser]


class DetailPharmacyProduct(RetrieveUpdateDestroyAPIView):
    queryset = PharmacyProduct.objects.all()
    serializer_class = PharmacyProductSerializer
    permission_classes = [permissions.IsAdminUser]


# Pharmacy catalog
class PharmacyCatalogView(ListAPIView):
    queryset = PharmacyProduct.objects.filter(is_active=True)
    serializer_class = PharmacyProductSerializer
    permission_classes = [permissions.IsAuthenticated]

