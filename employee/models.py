from django.db import models
import datetime
import random
from fields.models import FieldMapping


##For Saving Doc
class Document(models.Model):
	docfile = models.FileField(upload_to='documents')
	

###-------------------Departments----------

#-========================================
class AddDepartment(models.Manager):	
	def checkdept(self,row,IDKey,time):
		#for each - check if employee exists
			Dept = self.filter(DeptID=row[IDKey])
			if Dept.count()==0:
				bar = Department(
                        DeptID = row[IDKey],	
                        LastChangeDate = time
                )
				bar.save()
				return('added')
			else:
				return('existing')
			

class Department(models.Model):
	DeptID = models.CharField(max_length=400,default="N/A",primary_key=True)
	LastChangeDate = models.DateField(("Date"))
	Object = AddDepartment()

	def _str_(self):
		return self.DeptID


class AddDeptAttrs(models.Manager):
	def addNewEntry(self,id, e_date):
		#add prelim entryconfigure dates
		
		prevattrs = DepartmentAttrs.Object.filter(Dept=id)
		islatest = True
		maxprevdate = datetime.datetime.strptime("01011900","%d%m%Y")
		minnextdate = datetime.datetime.strptime("01013000","%d%m%Y")
		nextObj = []
		prevObj = []
		prevcounter = 0
		
		for entry in prevattrs:
			checkdate = datetime.datetime.combine(entry.AsofDate,datetime.datetime.min.time())#convert 
			#date_next = datetime.datetime.combine(entry.NextDate,datetime.datetime.min.time())#convert 

			if (checkdate < e_date) & (checkdate > maxprevdate):
				maxprevdate = checkdate
				prevObj = entry
				if entry.IsMostRecent == True:
					entry.IsMostRecent == False
					entry.save()
			elif (checkdate > e_date) & (checkdate < minnextdate):
				minnextdate = checkdate
				nextObj = ed	
				islatest = False
			elif checkdate == e_date:  #date already exists, remove to avoid duplication
				entry.delete()

		if prevObj!=[]:
			prevObj.NextDate = e_date
			prevObj.IsMostRecent = False
			prevObj.save()


		deptObj = Department.Object.get(DeptID=id)
		randstring = hex(random.getrandbits(16))
		attr = DepartmentAttrs(
			AttrKey=deptObj.DeptID+randstring,
			Dept = deptObj,
			AsofDate = e_date,
			IsMostRecent = islatest
		)
		attr.save()
		return(attr)


class DepartmentAttrs(models.Model):
	AttrKey = models.CharField(max_length=100,primary_key=True,default="N/A")
	Dept = models.ForeignKey(Department,related_name="enc_deptdate",on_delete=models.CASCADE)
	DepartmentName = models.CharField(max_length=200,default="N/A")
	AsofDate = models.DateField(("Date"))
	NextDate = models.DateField(("Date"),default=datetime.datetime(3300,1,1))
	IsMostRecent = models.BooleanField()
	Attribute1 = models.CharField(max_length=400,default="N/A")
	Attribute2 = models.CharField(max_length=400,default="N/A")
	Attribute3 = models.CharField(max_length=400,default="N/A")
	Attribute4 = models.CharField(max_length=400,default="N/A")	
	Object = AddDeptAttrs()



#-========================================
class EmpModel(models.Model):
	ModelName = models.CharField(max_length=100,default="Default",primary_key=True)
	CreateDate = models.DateField(("Date"))	


class AddEmployee(models.Manager):	
	def checkEmp(self,row,IDKey,NameKey,time):
		#for each - check if employee exists
			Emp = self.filter(EmpID=row[IDKey])
			if Emp.count()==0:
				bar = Employee(
                        EmpID = row[IDKey],	
                        Name = row[NameKey],
                        CreateDate = time
                )
				bar.save()
				print("Added " + row[NameKey])
				return('hire')
			else:
				return('entry')


class Employee(models.Model):
	EmpID = models.CharField(max_length=20,default="N/A",primary_key=True)
	Name = models.CharField(max_length=200,default="N/A")
	CreateDate = models.DateField(("Date"))
	EmailAddress = models.CharField(max_length=100,default="N/A")
	Object = AddEmployee()

	def _str_(self):
		return self.EmpID


REPORTS = (('hire','HIRE'),('term','TERMINATION'),('entry','Entry'),('transfer','TRANSFER'),('promo',"PROMOTION"))

#Dates - will be updated when employee record in the middle of the timeline is added/changed
class EmpDates(models.Model):
	EmpDateKey = models.CharField(max_length=100,primary_key=True)
	EmpID = models.ForeignKey(Employee,related_name='encryptEmpDate',on_delete=models.CASCADE)
	ModelKey = models.ForeignKey(EmpModel,related_name="empdate_model",default="Default", on_delete=models.CASCADE)
	CurrDate = models.DateField(("Date"))
	PrevDate = models.DateField(("Date"),default=datetime.datetime(1900,1,1))
	NextDate = models.DateField(("Date"),default=datetime.datetime(3300,1,1))
	Status = models.CharField(max_length=50,choices=REPORTS, default="entry")



#list of employees at different times
class Employee_State(models.Model):
	EmpID = models.ForeignKey(Employee,related_name='encryptEmp',on_delete=models.CASCADE)
	EmpDate = models.ForeignKey(EmpDates,related_name="enc_date_state", on_delete=models.CASCADE)
	Name = models.CharField(max_length = 200,default="N/A")
	ModelKey = models.ForeignKey(EmpModel,related_name="emp_model",default="Default", on_delete=models.CASCADE) #to group entries
	Status = models.CharField(max_length=50,choices=REPORTS, default="entry")
	Date = models.DateField(("Date"),default=datetime.datetime(1900,1,1))
	JobCode = models.CharField(max_length=120,default="N/A")
	Salary = models.DecimalField(max_digits=10,decimal_places=2,default=0)
	#DepartmentID = models.ManyToManyField(Department)
	ReportsToID = models.ForeignKey(Employee, related_name='enc_reports',on_delete=models.SET_NULL, null=True)
	DeptID = models.ForeignKey(Department,related_name="emp_dept",default="N/A", on_delete=models.SET_DEFAULT)
	Location = models.CharField(max_length=120,default="N/A")
	ServiceLine = models.CharField(max_length=120,default="N/A")
	Embedding1 = models.DecimalField(max_digits=10,decimal_places=6,default=0)
	Embedding2 = models.DecimalField(max_digits=10,decimal_places=6,default=0)


class RuleModel(models.Model):
	ModelName = models.CharField(max_length=100,primary_key=True)
	CreateDate = models.DateField(("Date"))
	
	def _str_(self):
		return self.ModelName


class Ruleset(models.Model):
	OPERATION = (('and',"and"),('or',"or"))

	Model = models.ForeignKey(RuleModel,related_name="enc_ruleset",on_delete=models.CASCADE)
	RuleKey = models.CharField(max_length=50,primary_key=True)
	Operation = models.CharField(max_length=50,choices=OPERATION, default="and")
	#Field1 = models.CharField(max_length = 100,default="N/A")
	#Field2 = models.CharField(max_length = 200,default="N/A")
	Field1 = models.ForeignKey(FieldMapping,related_name="enc_rulefield1",default="", on_delete=models.CASCADE)
	Field2 = models.ForeignKey(FieldMapping,related_name="enc_rulefield2",default="", on_delete=models.CASCADE,db_constraint=False)


	def _str_(self):
		return self.RuleKey


class Exception(models.Model):
	Rule = models.ForeignKey(Ruleset,related_name="enc_exception",on_delete=models.CASCADE)
	ExceptionVal = models.CharField(max_length=300)
	FieldNo = models.IntegerField(default=0)