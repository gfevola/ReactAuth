#authsystem_new/employee/urls
from rest_framework import routers
from django.urls import path, include
from .views import (DataView, DataViewPost, EmpModelView, EmpStateView, EmpModelDelete,
                    RuleModelPost, RulePost, RulesetImportView,
                    RuleModelDelete, RuleDelete, 
                    DepartmentView, DepartmentPost, DepartmentFilter, DeptAttrCurrentView, DataChange)

#router = routers.DefaultRouter()

urlpatterns = [
    #path('',include(router.urls)),
    path('data',DataView.as_view()),
    path('datapost',DataViewPost.as_view()),

    #path('empsingledate', EmpStateView.as_view()),
    path('empmodel',EmpModelView.as_view()),    
    path('empmodeldelete',EmpModelDelete.as_view()),
    
    path('rulemodel',RuleModelPost.as_view()),
    path('rulepost',RulePost.as_view()),
    path('rulesets',RulesetImportView.as_view()),
    path('rulemodeldelete',RuleModelDelete.as_view()),
    path('ruledelete',RuleDelete.as_view()),    

    path('deptview',DepartmentView.as_view()),
    path('deptcurrview',DeptAttrCurrentView.as_view()),
    path('deptpost',DepartmentPost.as_view()),
    path('deptfilt',DepartmentFilter.as_view()),
    path('datachg',DataChange.as_view()),

    #path('upload/',EmpTemplateView, name="upload-emp"),   
]