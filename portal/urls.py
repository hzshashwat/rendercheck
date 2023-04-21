from django.urls import path, include
from portal.views import *

urlpatterns = [
    path('importusers/', UsersImport.as_view()),
    path('login/', UserLoginApiView.as_view()),
]
