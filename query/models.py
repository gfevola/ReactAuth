from django.db import models
import datetime
from employee.models import RuleModel 

class QueryModel(models.Model):
    CHARTS = (('Table',"Table"),("Bar","Bar"),('Line','Line'),('Bubble','Bubble'))
    REPORTS = (('Hire','Hire'),('Term','Term'),('demographic','Demographic'),('Promo',"Promo"))
    PERIODS = (("None","None"),("Weekly","Weekly"),("Monthly","Monthly"),("Yearly","Yearly"))

    ModelName = models.CharField(max_length=400,default="N/A",primary_key=True)
    ChartType = models.CharField(max_length=50,choices=CHARTS, default="Table")
    Status = models.CharField(max_length=50,choices=REPORTS, default="entry")
    XFieldName = models.CharField(max_length=400,default="N/A")
    RuleModelName = models.ForeignKey(RuleModel,related_name="enc_qryrule",on_delete=models.CASCADE,null=True)
    AsofDate = models.DateField(("Date"),default=datetime.datetime.today())
    NPeriods = models.IntegerField(default=0) 
    Period = models.CharField(max_length=50,choices=PERIODS,default="None")
    FieldBand = models.IntegerField(default=0)

    @classmethod
    def GetDate(self, date1):
        return([self.Status,date1])

class BasicQuery(models.Model):
    ModelName = models.ForeignKey(QueryModel,related_name="enc_basic",on_delete=models.CASCADE)
    DateVar = models.DateField(("Date"),default=datetime.datetime(1900,1,1))
    Variable = models.CharField(max_length=400,default="N/A")
    Value = models.CharField(max_length=400,default="N/A")

