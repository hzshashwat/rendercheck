from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views import View
import requests
import json

# Create your views here.
class UsersImportAPIView(View):
    def get(self, request):
        api_request = requests.get("https://blockverseapi.onrender.com/teamData")
        try:
            data = json.loads(api_request.content)
            no_of_entries = len(data)
            list = []
            for i in range(0, no_of_entries-1):
                x = data[0]['_id']
                list.append(x)
            return HttpResponse(str(list))
        except Exception as e:
            return HttpResponse(str(e))