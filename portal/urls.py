from django.urls import path, include
from portal.views import *

urlpatterns = [
    path('registration/', Registration.as_view()),
    # path('clogin/', CustomAuthToken.as_view()),
    path('login/', GoogleOAuth.as_view()),
    path('schema_list/', SchemaList.as_view()),
    path('asset_list/', AssetList.as_view()),
    path('score/', ScoreApiViewSet.as_view()),
    path('leaderboard/', LeaderBoardAPIView.as_view()),
    path('schema_selection/', SchemaSelection.as_view()),
    path('submit/', FinalSubmission.as_view())
]
