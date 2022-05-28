#authsystem_new/fields/views
from django.shortcuts import render
from django.conf import settings
from .models import  FieldMapping
from .serializers import FieldMappingSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

from employee.models import Document, Employee_State, DepartmentAttrs

# Create your views here.
import pandas as pd
import numpy as np
from datetime import datetime
import random



##---------------fields----------------
#get fields data
class FieldMapPost(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request, format=None):
        data = self.request.data
        UploadField(data,data['iskeyfield'])
        return(Response("completed"))

class FieldMapPostKeys(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request, format=None):
        data = self.request.data 
        datafile = SaveFile(data['file'])
        for i, rw in datafile.iterrows():
            UploadField(rw,rw['iskeyfield'])
        return(Response("finished"))

def UploadField(data,iskeyfield):
    key = randstring = hex(random.getrandbits(16))
    iskeyfield = Str_to_bool(iskeyfield)

    fld = FieldMapping(
        Key = key,
        ModelName = data['category'],
        AttrName = data['attrName'],
        IsKeyField = iskeyfield,
        FieldName = data['fieldName'],
        HeaderName = data['headerName']
    )
    fld.save()

#field data retrieve
class FieldMapRetrieveView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data
        if data['modelcategory']=="*":
            queryset = FieldMapping.objects.all()  
        else:
            queryset = FieldMapping.objects.filter(ModelName=data['modelcategory'])  
        serializer_class = FieldMappingSerializer(queryset,many=True)
        return(Response(serializer_class.data))



class SingleFieldValues(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data
        print(data)
        field = FieldMapping.objects.get(FieldName=data['fieldname'])

        if field.ModelName=="EmployeeState":
            newdata = Employee_State.objects.values_list(field.FieldName).distinct() #.distinct(field.FieldName)
        elif field.ModelName=="Department":
            newdata = DepartmentAttrs.Object.values_list(field.FieldName).distinct() #.distinct(field.FieldName)
        #elif: field.ModelName=="JobTable":

        return(Response(newdata))   


#_----------------------
##copy from employee.views
def SaveFile(file):
    newfile = Document(docfile=file)
    newfile.save()
    
    path = settings.MEDIA_ROOT.replace("\\","/") + "/" + str(newfile.docfile)
    data = pd.read_excel(path)
    return(data)


import six
def Str_to_bool(str1):
    if isinstance(str1,six.string_types):
        if str1.lower() == "false":
            val=False
        elif str1.lower() == "true":
            val=True
    else:
        val = str1
    return val


