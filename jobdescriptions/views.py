from django.shortcuts import render
from django.conf import settings
from .models import JobTitles, DescGram, RelatedDesc
from employee.models import Document
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from rest_framework.response import Response
from .serializers import JobTitlesSerializer

import sys

sys.path.insert(0, './jobdescriptions/pythonscripts')
import pandas as pd
import JobDescriptions_Overall as jdo

class JDView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = JobTitlesSerializer
    queryset = JobTitles.objects.all()



class DataUpload(APIView):
    permission_classes = (permissions.AllowAny, )
    print('jdupload')

    def post(self, request, format=None):
        data = self.request.data
        ImportView(data['jdfile'])
        return Response({'note':'imported successfully'})


def ImportView(file):

    print(file)
    newfile = Document(docfile=file)
    newfile.save()

    path = settings.MEDIA_ROOT.replace("\\","/") + "/" + str(newfile.docfile)
    data_rawfile = pd.read_excel(path)

    [Data_JobTitles, Data_JobDesc, Data_Matches] = jdo.JobDescriptionsAnalyze(data_rawfile,"Job.ID",'Business.Title','Job.Description')

    #delete history
    history = JobTitles.objects.all()
    history.delete()

    for index, row in Data_JobTitles.iterrows():
        title = JobTitles(
            JobCode = row['Job.ID'],
            JobTitle = row['Business.Title'],
            Description = row['Job.Description'],
        )
        title.save()


    for index, row in Data_JobDesc.iterrows():
        Title = JobTitles.objects.get(JobCode=row['Job.ID'])
        try:
            desc = DescGram(
                    JobCodeKey = Title, #foreign key to jobtitle model					
                    GramKey = row['UniqueGramNo'] + "_" + row['Job.ID'],
                    GramIndicator = row['UniqueGramNo'],
                    Text = row['JDString'],
                    Category = row['Category'],
                    TopicNum = row['Topic'],
                    Embedding1 = row['X'],
                    Embedding2 = row['Y'],
                    Embedding3 = row['Z'],
                )
            desc.save()
        except:
            print(row)


    for index, row in Data_Matches.iterrows():
        print(row['UniqueGramNoFrom'])
        Primarygram = DescGram.objects.filter(GramIndicator=row['UniqueGramNoFrom'])
        try: #multiple items returned
            for obj in Primarygram:
                try:
                    match = RelatedDesc(
                        GramPrimary = obj,
                        GramRelated = row['UniqueGramNoTo']
                    )
                except:
                    print('error - '+row['UniqueGramNoFrom'])
        except: #single item
                try:
                    match = RelatedDesc(
                        GramPrimary = Primarygram,
                        GramRelated = row['UniqueGramNoTo']
                    )
                except:
                    print('error - '+row['UniqueGramNoFrom'])
    print('completed')
            
    return Response("complete")