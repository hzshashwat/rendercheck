from django.contrib import admin
from portal.models import UserProfile,  LeaderBoard, Schema, SchemaAsset
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(LeaderBoard)
admin.site.register(Schema)
admin.site.register(SchemaAsset)