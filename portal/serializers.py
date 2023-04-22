from rest_framework import serializers
from portal.models import *

class LeaderBoardSerializer(serializers.ModelSerializer):
    team = serializers.EmailField(read_only=True)
    team_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    score = serializers.IntegerField(required=False)
    class Meta:
        model = LeaderBoard
        fields = ['team', 'team_name', 'score']
        extra_kwargs = {'team' : {'read_only' : True}}