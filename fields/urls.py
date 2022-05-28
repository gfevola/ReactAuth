#authsystem_new/employee/urls
from rest_framework import routers
from django.urls import path, include
from .views import (FieldMapPost, FieldMapRetrieveView, FieldMapPostKeys,SingleFieldValues)

#router = routers.DefaultRouter()

urlpatterns = [
    #path('',include(router.urls)),
    path('fieldretrieve', FieldMapRetrieveView.as_view()),
    path('fieldpost',FieldMapPost.as_view()),
    path('fieldkeypost',FieldMapPostKeys.as_view()),
    path('fieldvalues',SingleFieldValues.as_view())
]