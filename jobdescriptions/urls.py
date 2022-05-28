#completeversion/data/urls
from rest_framework import routers
from django.urls import path, include
from .views import DataUpload, JDView


urlpatterns = [
    path('dataupload/',DataUpload.as_view()),
    path('data/',JDView.as_view())
]


