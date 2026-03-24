from django.shortcuts import render
from rest_framework.generics import CreateAPIView,ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions


from .models import PharmacyCategory, PharmacyProduct
from .serializers import PharmacyCategorySerializer
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




#send your CV