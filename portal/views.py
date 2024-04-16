from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from portal.models import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from portal.serializers import *
from datetime import datetime, timezone, timedelta
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from threading import Lock
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from PIL import Image
import io, json, os, requests, base64

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
            APIPin = data['APIPin']

            if(APIPin == "7jkshcs3GH"):
                pass
            else:
                return Response({"message" : "User Kicked Out"})
            
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
    

driver = None
model = None
lock = Lock()

def get_driver():
    global driver
    with lock:
        if driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1024,1440")
            chrome_service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver

def get_model():
    global model
    with lock:
        if model is None:
            model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    return model

def preprocess(image_data):
    img = Image.open(io.BytesIO(image_data)).resize((224, 224))
    x = np.array(img)
    if x.ndim == 2:
        x = np.stack((x,)*3, axis=-1)
    elif x.shape[2] == 4:
        x = x[..., :3]
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x

def image_similarity(img_data1, img_data2):
    model = get_model()
    img1 = preprocess(img_data1)
    img2 = preprocess(img_data2)
    features1 = model.predict(img1)
    features2 = model.predict(img2)
    features1 = features1.flatten()
    features2 = features2.flatten()
    similarity_score = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
    return similarity_score

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
            event_start_time = datetime(2023, 5, 28, 9, 20, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))

            current_time = datetime.now(timezone(timedelta(hours=5, minutes=30)))
            time_taken = current_time - event_start_time
            total_seconds = int(time_taken.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            time_taken_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            score.time_taken = time_taken_str
            
            # Selenium Code
            driver = get_driver()

            data = request.data
            html_code = data['html_code']
            css_code = data['css_code']
            html = "<html><head><style>" + str(css_code) + "</style></head><body>" + str(html_code) + "</body></html>"
            driver.get(f"data:text/html;charset=utf-8,{html}")
            screenshot1 = driver.get_screenshot_as_png()

            # Load an image from the root directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, 'test.png')
            with open(image_path, 'rb') as image_file:
                screenshot2 = image_file.read()

            similarity = image_similarity(screenshot1, screenshot2)
            mlmodel_output = round(similarity * 100)

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