#authsystem_new/query/views
from django.shortcuts import render
from django.conf import settings
from .serializers import *

from employee.models import *
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Q

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class BasicQueryView(ListAPIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):  
        data = self.request.data         
        querydata = QueryModel.objects.get(ModelName=data['ModelName'])
        serizalizer_class = QueryModelSerializer(querydata)
        return(Response(serizalizer_class.data))   

class BasicQueryPost(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):  
        data = self.request.data 
        print(data)
        #model setup
        [dt_lower, dt_higher] = Qry_ManageDateRange(data['dateSpread'], int(data['nperiods']), 
                                                data['period'], int(data['ed_year']), 
                                                int(data['ed_month']), int(data['ed_day']))
        qrymodel = SaveQueryModel(data,dt_higher)

        #field names
        try:
            fieldobj = FieldMapping.objects.get(Key=qrymodel.XFieldName)
            fieldX = {'ModelName': fieldobj.ModelName, 'AttrName': fieldobj.AttrName}
            groupcol = fieldX['AttrName']
        except:
            fieldX = {'ModelName':'EmployeeState','AttrName':'Datetrim'}   
            groupcol = 'none'  

        if data['rule']!='':
            rulelist = DataTableParse(data['rule'],5)
        
        runcount = 1
        if (data['dateSpread']=="spread") & (qrymodel.Status=="demographic"): runcount = qrymodel.NPeriods
        if (data['dateSpread']=="range"): 
            dt_lower = datetime(int(data['bg_year']),int(data['bg_month']),int(data['bg_day']))
        
        #pull query
        lw = dt_higher
        hi = dt_higher  
        querylist = pd.DataFrame() 
        for n in range(runcount):
            #demographic version
            if data['reportType']=="demographic":
                [lw, hi] = Qry_ManageDateRange(data['dateSpread'], 1, data['period'], lw.year, lw.month, lw.day)
                queryemp = (Employee_State.objects.filter(EmpDate__CurrDate__lte=hi)
                    .filter(EmpDate__NextDate__gt =hi)
                    .exclude(EmpDate__Status__in=["Term"])
                )
            else:
                queryemp = (Employee_State.objects.filter(EmpDate__CurrDate__lte=dt_higher)
                    .filter(EmpDate__CurrDate__gt = dt_lower)
                    .filter(EmpDate__Status__in=[data['reportType']])
                )

            #rulesets
            if data['rule']!='':
                queryset = ApplyRulesets(queryemp,rulelist)

            querydata = pd.DataFrame(queryemp.values())
            querydata.columns = [c.replace("_id","") for c in querydata.columns]
            querydata['DateVar'] = hi
            querylist = pd.concat([querylist,querydata],axis=0)    


        print(len(querylist))
        if len(querylist) > 0: #continue

            if fieldX['ModelName']=="EmployeeState":
                #just employee state model - no table joins
                querymg = querylist

            if fieldX['ModelName']=="Department":
                #integrate department
                if data['MostRecentMapping']=="False":
                    querydept = DepartmentAttrs.Object.filter(AsofDate__lte=dt_higher).filter(NextDate__gt=dt_higher)
                else:
                    querydept = DepartmentAttrs.Object.filter(IsMostRecent==True)
                querydept = pd.DataFrame(querydept.values())
                querydept.columns = [c.replace("_id","") for c in querydept.columns]

                querymg = pd.merge(querylist,querydept,how="left",left_on="DeptID",right_on="Dept")
            
            querymg['none'] = ""
            #change group field based on field banding max
            if (qrymodel.FieldBand>0):# & (groupcol!="none"):
                counts = querymg.groupby(groupcol).count().reset_index()
                counts = counts[[groupcol,'id']].reset_index()
                counttop = counts['id'].nlargest(qrymodel.FieldBand).reset_index()
                counts_groups = counts.merge(counttop,how="left",left_on="index",right_on="index")
                counts_groups['RevisedGrouping'] = counts_groups[groupcol]
                counts_groups['RevisedGrouping'] = np.where(np.isnan(counts_groups["id_y"]),"Other",counts_groups['RevisedGrouping'])
                counts_groups = counts_groups[[groupcol,"RevisedGrouping"]]
                querymg = querymg.merge(counts_groups,how="left",left_on=groupcol,right_on=groupcol)
            else:
                querymg['RevisedGrouping']=querymg[groupcol]

            #pivot data into querymodel
            #create rounded dates
            if (data['dateSpread']=="spread") & (qrymodel.Status!='demographic'): #PAD, by date
                if qrymodel.Period=="Monthly":
                    c = dt_higher.day #correction factor, zero out if rounding down
                    querymg['DateVar'] = querymg['Date'].apply(lambda x: x - timedelta((x - timedelta(c)).day))
                elif qrymodel.Period=="Weekly":
                    c = dt_higher.weekday() #correction factor, zero out if rounding down
                    querymg['DateVar'] = querymg['Date'].apply(lambda x: x - timedelta((x - timedelta(c)).weekday()))
                elif qrymodel.Period=="yearly":
                    c = dt_higher.timetuple().tm_yday #correction factor, zero out if rounding down
                    querymg['DateVar'] = querymg['Date'].apply(lambda x: x - timedelta((x - timedelta(c)).timetuple().tm_yday))
                else:
                    querymg['DateVar'] = querymg['Date'] ##shouldn't come up
                    print("period case default")

            querysum = querymg.groupby(['RevisedGrouping','DateVar'])['EmpID'].count().reset_index()
            querysum.columns = ['Variable','DateVar',"Value"]

            SaveBasicQuery(querysum,data['ModelName'])

            querydata = QueryModel.objects.get(ModelName=data['ModelName'])
            serizalizer_class = QueryModelSerializer(querydata)

            return(Response(serizalizer_class.data))   
        else:
            return(Response("Nothing"))

def SaveQueryModel(data,dt):

    DeleteModel(data['ModelName'],model=QueryModel,field='ModelName')

    model = QueryModel(
        ModelName = data['ModelName'],
        ChartType = data['chartType'],
        Status = data['reportType'],
        XFieldName = data['Xval'],
        AsofDate = dt,
        NPeriods = int(data['nperiods']),
        Period = data['period'],
        FieldBand = int(data['fieldBand'])
    )
    model.save()

    try:
        rulemdl = RuleModel.objects.get(ModelName=data['ruleModelName'])
        model.RuleModelName = rulemdl
        model.save()
    except:
        print("no rule model")    

    return(model)


def SaveBasicQuery(querydata,modelname):
    model = QueryModel.objects.get(ModelName=modelname)
    for i, row in querydata.iterrows():
        qry = BasicQuery(
            ModelName = model,
            DateVar = row['DateVar'],
            Variable = row['Variable'],
            Value = row['Value']
        )
        qry.save()    



#############helper functions
def DeleteModel(keystring, *args, **kwargs):

    models1 = kwargs['model'].objects.filter(ModelName=keystring)
    #models = kwargs['model'].objects.filter(**{'{}__in'.format(kwargs['field']): keystring})
    if models1.count()==1:
        history = kwargs['model'].objects.get(ModelName=keystring)
        history.delete()
        print('deleted model')
    else: 
        print('no model')
        pass
    return("deleted")

def DataTableParse(data,ncols):
    datasplit = pd.Series(data.split(","))
    datasplit = datasplit.apply(lambda x: x.replace("|||",",")) #hardcoded key string ||| to prevent splitting of internal commas
    rownum = int(len(datasplit)/ncols)
    datalist = datasplit.values.reshape(rownum,ncols)
    return(datalist)

    
def ApplyRulesets(querydata,ruledata):
    rulesField1 = []
    rulesField2 = []
    rule1 = []
    rule2 = []
    currint = 0
    maxint = 0
    operators = []

    for r in ruledata:
        print(r)
        if currint!= int(r[0]):
            currint = int(r[0])
            maxint = maxint + 1
            rulesField1.append([fld1,rule1])
            rulesField2.append([fld2,rule2])
            rule1 = []
            rule2 = []
            operators.append(oper)
        if r[1]=="1":
            rule1.append(r[3])
            fld1 = FieldMapping.objects.get(Key=r[2]).FieldName
        else:
            rule2.append(r[3])
            fld2 = FieldMapping.objects.get(Key=r[2]).FieldName
        oper = r[4]

    maxint = maxint+1
    rulesField1.append([FieldMapping.objects.get(Key=r[2]).FieldName,rule1])
    rulesField2.append([FieldMapping.objects.get(Key=r[2]).FieldName,rule2])
    print(rulesField1)
    print(rulesField2)
    operators.append(oper)

    for i in range(maxint):
        filtrule1 = rulesField1[i]
        filtrule2 = rulesField2[i]
        oper = operators[i]
        print(filtrule1)
        print(filtrule2)
        if oper == "and":
            qry3 = querydata.exclude( **{'{}__in'.format(filtrule1[0]): filtrule1[1] } ).exclude( **{'{}__in'.format(filtrule2[0]): filtrule2[1] } )
        elif oper == "or":
            qry3 = querydata.exclude( Q(**{'{}__in'.format(filtrule1[0]): filtrule1[1] } ) | Q( **{'{}__in'.format(filtrule2[0]): filtrule2[1] } ))  
    return(qry3)



def Qry_ManageDateRange(dateSpread, nperiods, period, yr, mo, dy):
        #date range
        dt_higher = datetime(yr,mo,dy)
        dt_lower = dt_higher
        if dateSpread == "spread":
            if period == "Weekly":
                dt_lower = dt_higher - timedelta(days=7 * nperiods)
            elif period == "Monthly":
                tot_months = mo + 12*yr
                years = int(np.floor((tot_months - nperiods)/12))
                months = int(np.round(((tot_months - nperiods-1)/12 - years) * 12,0))+1
                if months==0: months = 12
                dt_lower = datetime(years,months,dy)
            elif period == "Yearly":             
                dt_lower = datetime(yr - nperiods,mo, dy)
        return([dt_lower,dt_higher])