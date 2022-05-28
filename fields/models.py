from django.db import models

# Create your models here.

class FieldMapping(models.Model):

	MODELS = (('EmployeeState',"EmployeeState"),("Department","Department"),('JobTable','JobTable'))
	DATATYPES = (('Text',"Text"),('Number',"Number"),('Freeform',"Freeform"))
	Key = models.CharField(max_length=100,primary_key=True,default="N/A")
	ModelName = models.CharField(max_length=40,choices = MODELS, default="")
	AttrName = models.CharField(max_length=100,default="")
	IsKeyField = models.BooleanField(default=False)
	FieldName = models.CharField(max_length=100,default="")
	HeaderName = models.CharField(max_length=100,default="")
	DataType = models.CharField(max_length=100,choices = DATATYPES, default="Text")

	def _str_(self):
		return self.FieldName
