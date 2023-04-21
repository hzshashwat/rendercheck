from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views import View
import requests
import json
from portal.models import *

# Create your views here.
class UsersImport(View):
    def get(self, request):
        api_request = requests.get("https://blockverseapi.onrender.com/teamData")
        try:
            data = json.loads(api_request.content)
            no_of_entries = len(data)

            for i in range(0, no_of_entries):
                team_name = data[i]['team_name']
                leader_name = data[i]['leader_name']
                leader_email = data[i]['leader_email']
                leader_hosteler = data[i]['leader_hosteler']
                leader_year = data[i]['leader_year']
                leader_branch = data[i]['leader_branch']
                leader_rollNo = data[i]['leader_rollNo']
                leader_phoneNo = data[i]['leader_phoneNo']
                member_name = data[i]['member_name']
                member_phoneNo = data[i]['member_phoneNo']
                member_branch = data[i]['member_branch']
                member_email = data[i]['member_email']
                member_rollNo = data[i]['member_rollNo']
                member_hosteler = data[i]['member_hosteler']
                member_year = data[i]['member_year']
                password = data[i]['password']

                UserProfile.objects.create_user(leader_email = leader_email, password=password)

                user = UserProfile.objects.get(leader_email = leader_email)

                user.team_name = team_name
                user.leader_name = leader_name
                user.leader_hosteler = leader_hosteler
                user.leader_year = leader_year
                user.leader_branch = leader_branch
                user.leader_rollNo = leader_rollNo
                user.leader_phoneNo = leader_phoneNo
                user.member_name = member_name
                user.member_phoneNo = member_phoneNo
                user.member_branch = member_branch
                user.member_email = member_email
                user.member_rollNo = member_rollNo
                user.member_hosteler = member_hosteler
                user.member_year = member_year

                user.save()

                # user = UserProfile.objects.create(, password = password)

            return HttpResponse("Import Completed")
        
        except Exception as e:
            return HttpResponse(str(e))