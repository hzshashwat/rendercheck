from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views import View
import requests
import json
from portal.models import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from portal.serializers import *

# Create your views here.
class UsersImport(View):
    def get(self, request):
        api_request = requests.get("https://blockverseapi.onrender.com/teamData")
        try:
            data = json.loads(api_request.content)
            no_of_entries = len(data)

            for i in range(0, no_of_entries):

                # if data[i]['team_name'] is not None:
                #     team_name = data[i]['team_name']
                # else:
                #     team_name = " "

                # if data[i]['leader_name'] is not None:
                #     leader_name = data[i]['leader_name']
                # else:
                #     leader_name = " "
                    
                # if data[i]['leader_email'] is not None:
                #     leader_email = data[i]['leader_email']
                # else:
                #     leader_email = " "
                
                # if data[i]['leader_hosteler'] is not None:
                #     leader_hosteler = data[i]['leader_hosteler']
                # else:
                #     leader_hosteler = " "

                # if data[i]['leader_year'] is not None:
                #     leader_year = data[i]['leader_year']
                # else:
                #     leader_year = " "

                # if data[i]['leader_branch'] is not None:
                #     leader_branch = data[i]['leader_branch']
                # else:
                #     leader_branch = " "
                    
                # if data[i]['leader_rollNo'] is not None:
                #     leader_rollNo = data[i]['leader_rollNo']
                # else:
                #     leader_rollNo = " "
                    
                # if data[i]['leader_phoneNo'] is not None:
                #     leader_phoneNo = data[i]['leader_phoneNo']
                # else:
                #     leader_phoneNo = " "                    

                # if data[i]['member_name'] is not None:
                #     member_name = data[i]['member_name']
                # else:
                #     member_name = "Not provided"
                                        
                # if data[i]['member_phoneNo'] is not None:
                #     member_phoneNo = data[i]['member_phoneNo']
                # else:
                #     member_phoneNo = "Not provided"
                                        
                # if data[i]['member_branch'] is not None:
                #     member_branch = data[i]['member_branch']
                # else:
                #     member_branch = "Not provided"
                                        
                # if data[i]['member_email'] is not None:
                #     member_email = data[i]['member_email']
                # else:
                #     member_email = "Not provided"
                                        
                # if data[i]['member_rollNo'] is not None:
                #     member_rollNo = data[i]['member_rollNo']
                # else:
                #     member_rollNo = "Not provided"
                                        
                # if data[i]['member_hosteler'] is not None:
                #     member_hosteler = data[i]['member_hosteler']
                # else:
                #     member_hosteler = "Not provided"
                                                            
                # if data[i]['member_year'] is not None:
                #     member_year = data[i]['member_year']
                # else:
                #     member_year = "Not provided"

                # if data[i]['password'] is not None:
                #     password = data[i]['password']
                # else:
                #     password = ""


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

            return HttpResponse("Import Completed")
        
        except Exception as e:
            return HttpResponse(str(e))
        

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        print(request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        LeaderBoard.objects.create(team = user, team_name = user.team_name)

        return Response({
            'token': token.key,
            'email': user.leader_email
        })
    
class ScoreApiViewSet(APIView):
    serializer_class = LeaderBoardSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        try:
            team = LeaderBoard.objects.get(team = self.request.user)
            teamjson = LeaderBoardSerializer(team)
            return Response({"message" : [teamjson.data]})

        except Exception as e:
            return Response({"error": str(e)})

    def post(self, request):
        try :
            team = LeaderBoard.objects.get(team = self.request.user)
            teamobj = LeaderBoardSerializer(team, data=request.data)
            if teamobj.is_valid():
                teamobj.save()
                return Response({"message" : "Profile info updated."})
            else :
                return Response({"message": teamobj.errors,
                "status": "Failed"
                })
        except Exception as e:
            return Response({"error": str(e)})
        
