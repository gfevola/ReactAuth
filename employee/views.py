from django.shortcuts import render
from django.conf import settings
from .models import (Document, EmpModel, Employee, EmpDates, Employee_State,
                    RuleModel, Ruleset, Exception, Department, DepartmentAttrs)
from .serializers import (EmployeeSerializer, EmpDatesSerializer, 
                            RuleModelSerializer, RulesetSerializer, EmpStateSerializerTest,
                            DepartmentSerializer, DeptAttrsSerializer, EmpModelSerializer)
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Q

from fields.models import FieldMapping

# Create your views here.
import pandas as pd
import numpy as np
from datetime import datetime

class DataView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = EmployeeSerializer
    queryset = Employee.Object.filter().order_by('EmpID')


#-------------------------------------------------------------

##-employees
class DataView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = EmployeeSerializer
    queryset = Employee.Object.filter().order_by('EmpID')

class EmpModelView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = EmpModelSerializer
    queryset = EmpModel.objects.all() 

class EmpModelDelete(APIView):
    permission_classes = (permissions.AllowAny, )    
    def post(self, request, format=None):
        data = self.request.data
        print(data)
        try:
            mdl = EmpModel.objects.get(ModelName=data['modelname'])
            mdl.delete()
        except:
            print('emp model not found')
        return(Response("complete"))   


#for demographic point-in-time query
class EmpStateView(APIView):
    permission_classes = (permissions.AllowAny, ) 
    def post(self, request, format=None):
        data = self.request.data
        dt = datetime(data['year'],data['month'],data['day'])
        queryset = EmpDates.objects.filter(CurrDate__lte =dt).filter(NextDate__gt =dt).exclude(Status__in=["term"])
        serializer_class = EmpDatesSerializer(queryset,many=True)
        return(Response(serializer_class.data))        

#Upload (post) data to model
class DataViewPost(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data
        addeddepts = UploadEmpView(data['empFile'],data['repType'],data['modelname'])
        return(Response(addeddepts))

##----------------------------
#Rulesets/exceptions
class RulesetImportView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = RuleModelSerializer
    queryset = RuleModel.objects.all()


class RuleModelPost(APIView):
    permission_classes = (permissions.AllowAny, )    
    def post(self,request,format=None):
        data = self.request.data
        UploadCreateRuleModel(data['modelname'])
        return(Response("complete"))

class RulePost(APIView):
    permission_classes = (permissions.AllowAny, )    
    def post(self, request, format=None):
        data = self.request.data
        if len(data['exceptionsFile']) > 0:
            datalist = DataTableParse(data['exceptionsFile'],2)
            UploadRulesandExceptions(datalist, data['fieldkey1'], data['fieldkey2'],
                            data['ruleName'], data['andor'], data['modelName']) 
        else:
            print('no data')
        return(Response("complete"))


class RuleModelDelete(APIView):
    permission_classes = (permissions.AllowAny, )    
    def post(self, request, format=None):
        data = self.request.data
        try:
            mdl = RuleModel.objects.get(ModelName=data['modelName'])
            mdl.delete()
        except:
            print('model not found')
        return(Response("complete"))   

class RuleDelete(APIView):
    permission_classes = (permissions.AllowAny, )    
    def post(self, request, format=None):
        data = self.request.data
        print(data)
        try:
            mdl = RuleModel.objects.get(ModelName=data['modelName'])
            rule = Ruleset.objects.filter(Model=mdl).get(RuleKey=data['ruleName'])
            rule.delete()
        except:
            print('rule/model not found')
        return(Response("Deleted"))   

####################################


#-----departments -----------------------
class DepartmentPost(APIView):
    permission_classes = (permissions.AllowAny, )    
    def post(self, request, format=None):
        data = self.request.data
        dt = datetime(int(data['year']),int(data['month']),int(data['day']))
        data = SaveFile(data['data'])
        resp = UploadDepts(data,"DeptID",dt,True)
        return Response(resp)


class DepartmentFilter(APIView):
    #retrieve departments given a certain date
    permission_classes = (permissions.AllowAny, )
    def post(self, request, format=None):
        data = self.request.data
        dt = datetime(int(data['year']),int(data['month']),int(data['day']))
        queryset = Department.objects.filter(AsofDate__lte=dt)
        serializer_class = DeptAttrSerializer(filt,many=True)
        return(Response(serializer_class.data))     


class DepartmentView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = DepartmentSerializer
    queryset = Department.Object.all() 

class DeptAttrCurrentView(ListAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = DeptAttrsSerializer
    queryset = DepartmentAttrs.Object.filter(IsMostRecent=True) 

##variable model - for generic table add row
class DataChange(ListAPIView):
    #single datapoint
    permission_classes = (permissions.AllowAny, )
    def post(self, request, format=None):
        data = self.request.data
        print(data)
        dataparse = DataTableParse(data['data'],2)
        modelname = data['category']

        if modelname == "Department":
            obj = DepartmentAttrs.Object.get(AttrKey=data['id'])
        elif modelname == "FieldMapping":
            obj = FieldMapping.objects.get(Key=data['id'])
        for key,val in dataparse:
            setattr(obj, key, val)
        
        obj.save()

        return(Response("changed"))




#-----------------------------------------------------------------
#---------------------data functions------------------------------

def DataTableParse(data,ncols):
    datasplit = pd.Series(data.split(","))
    datasplit = datasplit.apply(lambda x: x.replace("|||",",")) #hardcoded key string ||| to prevent splitting of internal commas
    rownum = int(len(datasplit)/ncols)
    datalist = datasplit.values.reshape(rownum,ncols)
    return(datalist)

#example of filtering by secondary
def FieldFilterEmployee(querydata,criteria):
    filtstring = "DeptID__enc_deptdate__Location"
    y = Employee_State.objects.filter(**{'{}__in'.format(filtstring): criteria})



#-----------upload functions
def UploadDepts(data, idcol, asofdate, filldepts=True):
    addeddepts = []

    for i, row in data.iterrows():
        deptstatus = Department.Object.checkdept(row,idcol,datetime.now())

        if deptstatus == "added":
            addeddepts.append(row[idcol])

        if filldepts==True:
            mdl = Department.Object.get(DeptID=row[idcol])
            deptattr = DepartmentAttrs.Object.addNewEntry(row[idcol],asofdate) #need upload date
            deptattr.save()
            
            AddAttrs(row,deptattr,"Department")
            deptattr.save()

    return addeddepts


##----helper function - upload employee data--------------
def UploadEmpView(file, reporttype, modelname):

    DataFile = SaveFile(file)
    UploadCreateEmpModel(modelname)

    addeddepts = UploadDepts(DataFile, "DeptID", datetime.now(), filldepts=False) #date doesnt matter if false
    #Save Employee data
    for index, row in DataFile.iterrows():
        modelobj = EmpModel.objects.get(ModelName=modelname)
        try: #set up variables
            cdate = datetime.strptime(str(row['Date'])[0:10],"%Y-%m-%d")
            maxprevdate = datetime.strptime("01011900","%d%m%Y")
            minnextdate = datetime.strptime("01013000","%d%m%Y")
            nextObj = []
            prevObj = []
            prevcounter = 0
        except: #can't apply - next row
            print("date not found!")
            pass

        #logic
        sts = Employee.Object.checkEmp(row,"EmpID","Name",datetime.now())
        Emp = Employee.Object.get(EmpID=row['EmpID'])
        if sts == "entry": #newly added employee id
            edates = EmpDates.objects.filter(EmpID=Emp)
            #figure out previous entry
            for ed in edates:
                checkdate = datetime.strptime(str(ed.CurrDate),"%Y-%m-%d")
                if (checkdate < cdate) & (checkdate > maxprevdate):
                    maxprevdate = checkdate
                    prevObj = ed
                    prevcounter += 1
                elif checkdate == cdate:  #date already exists, remove to avoid duplication
                    ed.delete()
                elif (checkdate > cdate) & (checkdate < minnextdate):
                    minnextdate = checkdate
                    nextObj = ed

        dkey = str(row['EmpID']) + "_" + str(cdate)[0:10] + "_"

        #manage status further
        if prevcounter==0:
            sts = "hire"
        #override status with report value, if hire/term
        if reporttype=="Hires":
            sts = "hire"
        elif reporttype=="Terminations":
            sts = "term"
        elif reporttype=="Transfer":
            sts = "transfer"

        e_date = EmpDates(
            EmpDateKey = dkey,
            EmpID = Emp,
            ModelKey = modelobj,
            CurrDate = row['Date'],
            NextDate = minnextdate,
            Status = sts,
        )
        e_date.save()

        e_DateObj = EmpDates.objects.get(EmpDateKey=dkey)

        #fix related entries
        if prevObj!=[]:
            prevObj.NextDate = row['Date']
            prevObj.save()


        #mapping obj
        deptobj = Department.Object.get(DeptID=row['DeptID'])

        #default fields
        state = Employee_State(
                EmpID = Emp, #foreign key to employee model		
                EmpDate = e_DateObj,
                ModelKey = modelobj,
                DeptID = deptobj,
                Status = sts
            )
        state.save()

        AddAttrs(row, state,"EmployeeState")


    print('completed')
            
    return addeddepts


#----apply attributes (fields)
def AddAttrs(row, obj,modelCategory):
    fieldheaders = FieldMapping.objects.filter(ModelName=modelCategory).filter(IsKeyField=False)
    for fld in fieldheaders:
        try:
            setattr(obj, fld.AttrName, row[fld.HeaderName])
        except:
            print("error - " + fld.FieldName)
    obj.save()

#----
def UploadCreateEmpModel(ModelName):
    #function to add a model
    history = []
    try:
        history = EmpModel.objects.get(ModelName=ModelName)
    except:
        pass    
    if not history:
        model = EmpModel(
            ModelName = ModelName,
            CreateDate = datetime.now(),
        )
        model.save()

    return(Response("Complete"))  

def UploadCreateRuleModel(ModelName):
      #function to add/change a model
    try:
        history = RuleModel.objects.get(ModelName=ModelName)
        history.delete()
    except:
        pass  

    model = RuleModel(
        ModelName = ModelName,
        CreateDate = datetime.now(),
    )
    model.save()
    return(Response("Complete"))

####
def UploadRulesandExceptions(data, fieldkey1, fieldkey2, rulename, andor, ModelName):
    #function to add/change a specific rule
    print(data)
    try:
        history = Ruleset.objects.get(RuleKey=rulename)
        history.delete()
    except:
        pass

    model = RuleModel.objects.get(ModelName=ModelName)
    field1 = FieldMapping.objects.get(Key=fieldkey1)
    rule = Ruleset(
        Model = model,
        RuleKey = rulename,
        Operation = andor,
        Field1 = field1
      )
    if fieldkey2!='':
        field2 = FieldMapping.objects.get(Key=fieldkey2)
        rule.Field2 = field2

    rule.save()
    print('saved rule')

    ruleObj = Ruleset.objects.get(RuleKey=rulename)

    for rw in data:
        foo = Exception(
            Rule = ruleObj,
            ExceptionVal = rw[0],
            FieldNo = rw[1]
        )
        foo.save()
    print('saved rule & exceptions')
    return Response("complete")  


def SaveFile(file):
    newfile = Document(docfile=file)
    newfile.save()
    
    path = settings.MEDIA_ROOT.replace("\\","/") + "/" + str(newfile.docfile)
    data = pd.read_excel(path)
    return(data)

