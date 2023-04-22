from django.urls import path, include
from portal.views import *

urlpatterns = [
    path('importusers/', UsersImport.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('score/', ScoreApiViewSet.as_view()),
    path('leaderboard/', LeaderBoardAPIView.as_view()),
    path('schema_selection/', SchemaSelection.as_view()),
    path('submit/', FinalSubmission.as_view())
]
