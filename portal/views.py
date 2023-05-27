from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from portal.models import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from portal.serializers import *
import os
import requests
from datetime import datetime, timezone, timedelta
import json
from django.conf import settings
import base64

# Create your views here.
class Registration(APIView):
    def post(self, request):
        try:
            data = request.data

            team_name = data['team_name']
            leader_name = data['leader_name']
            leader_email = data['leader_email'].lower()
            leader_year = data['leader_year']
            member_name = data['member_name']
            member_email = data['member_email']
            member_year = data['member_year']
            
            password = "J72vgs9hbgf"


            UserProfile.objects.create_user(leader_email = leader_email, password=password)

            user = UserProfile.objects.get(leader_email = leader_email)

            user.team_name = team_name
            user.leader_name = leader_name
            user.leader_year = leader_year
            user.member_name = member_name
            user.member_email = member_email
            user.member_year = member_year

            user.save()

            return Response({"message" : "User Created"})
        
        except Exception as e:
            return Response({"message" : str(e)})
        

# class CustomAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)

#         try:
#             LeaderBoard.objects.create(team = user, team_name = user.team_name)
#         except:
#             pass
        
#         return Response({
#             'token': token.key,
#             'email': user.leader_email
#         })


class GoogleOAuth(APIView):
    def post(self, request):
        authorization_code = request.data.get('authorization_code')
        try:
            authorization_code_url = "https://oauth2.googleapis.com/token"

            payload = json.dumps({
            "code": authorization_code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code"
            })

            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", authorization_code_url, headers=headers, data=payload)
            
            access_token = response.json()['access_token']

            access_token_url = "https://www.googleapis.com/oauth2/v2/userinfo"

            payload = {}
            headers = {
            'Authorization': f'Bearer {access_token}'
            }

            response = requests.request("GET", access_token_url, headers=headers, data=payload)

            email = response.json()['email']

            if UserProfile.objects.filter(leader_email=email).exists():
                user = UserProfile.objects.get(leader_email = email)

                try:
                    final_submission = user.final_submission_completed
                    token = Token.objects.get(user=user)
                    token.delete()
                except Token.DoesNotExist:
                    pass
                token, created = Token.objects.get_or_create(user=user)

                try:
                    LeaderBoard.objects.create(team = user, team_name = user.team_name)
                except:
                    pass
                return Response({
                    'token': token.key,
                    'email': user.leader_email,
                    'final_submission' : final_submission
                })
            
            else:
                return Response({
                    "message" : "User not registered"
                })
            
        except Exception as e:
            return Response({'error' : str(e)})

class SchemaList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        try:
            team = UserProfile.objects.get(leader_email = self.request.user)
            year = team.leader_year

            schema_list = Schema.objects.filter(schema_year = year).all().values()
            return Response({"schema_list" : schema_list})
        except Exception as e:
            return Response({"error": str(e)})
        
class SchemaSelection(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, format= None):
        try:
            team = UserProfile.objects.get(leader_email = self.request.user)
            
            team.selected_schema = request.data['schema']
            team.save()
            return Response({"message" : "Schema Info Updated"})
        except Exception as e:
            return Response({"error" : str(e)})
        
class AssetList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        try:
            team = UserProfile.objects.get(leader_email = self.request.user)
            selected_schema = team.selected_schema

            asset_list = SchemaAsset.objects.filter(schema_id = selected_schema).all().values()
            return Response({"asset_list" : asset_list})
        except Exception as e:
            return Response({"error" : str(e)})
    
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
            data = request.data
            html_code = data["html_code"]
            css_code = data["css_code"]

            team = UserProfile.objects.get(leader_email = self.request.user)
            selected_schema = team.selected_schema

            # Rate Limiter Setup
            from django.core.cache import cache
            from django.core.cache.backends.base import DEFAULT_TIMEOUT

            if cache.get(team.leader_name):
                total_calls = cache.get(team.leader_name)
                if total_calls >= 1:
                    return Response({'status' : 501, 'message' : f'Request again after {cache.ttl(team.leader_name)} seconds'})
                else:
                    pass
            cache.set(team.leader_name, 1, timeout=75)


            score = LeaderBoard.objects.get(team = self.request.user)

            #Time Duration Logic
            event_start_time = datetime(2023, 5, 28, 9, 0, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))

            current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
            time_taken = current_time - event_start_time
            total_seconds = int(time_taken.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            time_taken_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            score.time_taken = time_taken_str
            
            #SCHEMAS
            # if selected_schema == 101:
            #     with open('Schemas/101.jpg', "rb") as image_file:
            #         encoded_image = base64.b64encode(image_file.read())
                
            # elif selected_schema == 102:
            #     with open('Schemas/102.jpg', "rb") as image_file:
            #         encoded_image = base64.b64encode(image_file.read())

            # elif selected_schema == 103:
            #     with open('Schemas/103.jpg', "rb") as image_file:
            #         encoded_image = base64.b64encode(image_file.read())

            # elif selected_schema == 201:
            #     with open('Schemas/test.png', "rb") as image_file:
            #         encoded_image = base64.b64encode(image_file.read())

            # elif selected_schema == 202:
            #     with open('Schemas/202.jpg', "rb") as image_file:
            #         encoded_image = base64.b64encode(image_file.read())

            # elif selected_schema == 203:
            #     with open('Schemas/203.jpg', "rb") as image_file:
            #         encoded_image = base64.b64encode(image_file.read())

            # base64_image = encoded_image.decode('utf-8')
            # schemaImageBase64 = str(base64_image)
            # print(schemaImageBase64)

            url = "http://13.126.103.160:8000/getSimiliarityV2"

            html = "<html><head><style>" + str(css_code) + "</style></head><body>" + str(html_code) + "</body></html>"

            payload = json.dumps({
            "html": html,
            "height": 1024,
            "width": 1440,
            "base64": False,
            "schemaID": selected_schema
            })
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            # print(response.text)

            content = response.json()
            mlmodel_output = content["similarity_score"]
            score.score = mlmodel_output
            score.save()
            return Response({'score' : mlmodel_output, 'time_taken' : time_taken_str})

        except Exception as e:
            return Response({"error": str(e)})
        
class LeaderBoardAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        try:
            team = LeaderBoard.objects.all().order_by('-score').values()
            return Response({"message" : team})

        except Exception as e:
            return Response({"error": str(e)})

class FinalSubmission(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, format= None):
        try:
            team = UserProfile.objects.get(leader_email = self.request.user)
            
            team.final_submission_completed = True

            # Save the HTML, CSS & JS files
            team_name = team.team_name
            team_name_underscored = team_name.replace(' ', '_')

            html_code = request.data['html_code']
            css_code = request.data['css_code']

            if not os.path.exists(f'Submitted_Code/{team_name_underscored}'):
                os.makedirs(f'Submitted_Code/{team_name_underscored}')

            with open(f'Submitted_Code/{team_name_underscored}/index.html', 'w') as f:
                f.write(html_code)
            with open(f'Submitted_Code/{team_name_underscored}/style.css', 'w') as f:
                f.write(css_code)

            team.save()
            return Response({"message" : "Submitted"})
        except Exception as e:
            return Response({"error" : str(e)})