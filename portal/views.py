from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from portal.models import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from portal.serializers import *
import os

# Create your views here.
class UsersImport(APIView):
    def post(self, request):
        try:
            data = request.data

            team_name = data['team_name']
            leader_name = data['leader_name']
            leader_email = data['leader_email']
            leader_year = data['leader_year']
            member_name = data['member_name']
            member_email = data['member_email']
            member_year = data['member_year']
            password = data['password']

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
        

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        try:
            LeaderBoard.objects.create(team = user, team_name = user.team_name)
        except:
            pass
        
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
        
class LeaderBoardAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        try:
            team = LeaderBoard.objects.all().values()
            return Response({"message" : team})

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

class FinalSubmission(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, format= None):
        try:
            team = UserProfile.objects.get(leader_email = self.request.user)
            
            team.final_submission_completed = request.data['submitted']

            # Save the HTML, CSS & JS files
            team_name = team.team_name
            team_name_underscored = team_name.replace(' ', '_')

            html_code = request.data['html_code']
            css_code = request.data['css_code']
            js_code = request.data['js_code']

            if not os.path.exists(f'Submitted_Code/{team_name_underscored}'):
                os.makedirs(f'Submitted_Code/{team_name_underscored}')

            with open(f'Submitted_Code/{team_name_underscored}/index.html', 'w') as f:
                f.write(html_code)
            with open(f'Submitted_Code/{team_name_underscored}/style.css', 'w') as f:
                f.write(css_code)
            with open(f'Submitted_Code/{team_name_underscored}/script.js', 'w') as f:
                f.write(js_code)

            team.save()
            return Response({"message" : "Submitted"})
        except Exception as e:
            return Response({"error" : str(e)})