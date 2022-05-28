#authsystem_new/query/urls
from rest_framework import routers
from django.urls import path, include
from .views import *

#router = routers.DefaultRouter()

urlpatterns = [
    path('basicpost',BasicQueryPost.as_view()),
    path('basicview',BasicQueryView.as_view()),    
]