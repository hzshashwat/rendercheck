from django.urls import path, include
from portal.views import *

urlpatterns = [
    path('importusers/', UsersImportAPIView.as_view())
]
