from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response


from .models import PharmacyCategory, PharmacyProduct
from .serializers import (
    PharmacyCategorySerializer,
    PharmacyProductSerializer,
    PharmacyOrderCreateSerializer,
    PharmacyOrderReadSerializer,
)

# Create your views here.


## Create CRUD for catagories
class CreateListPharmacyCategory(ListCreateAPIView):
    queryset = PharmacyCategory.objects.all()
    serializer_class = PharmacyCategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
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


# Order creation
class PharmacyOrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PharmacyOrderCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = PharmacyOrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            PharmacyOrderReadSerializer(order).data, status=status.HTTP_201_CREATED
        )
