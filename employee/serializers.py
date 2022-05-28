from rest_framework import serializers
from .models import (Employee, EmpModel, Employee_State, EmpDates,
					FieldMapping, RuleModel, Ruleset, Exception,
					Department, DepartmentAttrs)


class FieldMappingSerializer(serializers.ModelSerializer):
	class Meta:
		model = FieldMapping
		fields = "__all__"



###departments
class DeptAttrsSerializer(serializers.ModelSerializer):

	class Meta:
		model = DepartmentAttrs
		fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):

	attrs = DeptAttrsSerializer(read_only=True,source="enc_deptdate",many=True)

	class Meta:
		model = Department
		fields = "__all__"



class EmployeeStateSerializer(serializers.ModelSerializer):

	class Meta:
		model = Employee_State
		fields = "__all__"


class EmpDatesSerializer(serializers.ModelSerializer):

	state = EmployeeStateSerializer(read_only=True,source="enc_date_state",many=True)

	class Meta:
		model = EmpDates
		fields = ("EmpDateKey","EmpID","CurrDate","PrevDate",
		"NextDate", "Status", "state")

#test
class EmpStateSerializerTest(serializers.ModelSerializer):
	state = EmpDatesSerializer(read_only=True,source="enc_date_state",many=True)
	Dept2 = DepartmentSerializer(read_only=True,many=True)


	class Meta:
		model = Employee_State
		fields = ("EmpID","EmpDate","Name","ModelKey","Status","Date","JobCode","DeptID",'DepartmentID',"Dept2","state")
		#fields = ("EmpID","EmpDate","Name","Dept","Dept1")
		#depth = 1

class EmployeeSerializer(serializers.ModelSerializer):

	state = EmployeeStateSerializer(read_only=True,source="encryptEmp",many=True)

	class Meta:
		model = Employee
		fields = ("EmpID","Name","CreateDate","EmailAddress","state")

class EmpModelSerializer(serializers.ModelSerializer):
	class Meta:
		model = EmpModel
		fields = "__all__"


###rules and exceptions (subclass)
class ExceptionSerializer(serializers.ModelSerializer):

	class Meta:
		model = Exception
		fields = "__all__"


class RulesetSerializer(serializers.ModelSerializer):

	exceptions = ExceptionSerializer(read_only=True,source="enc_exception",many=True)
	FieldPrimary = FieldMappingSerializer(read_only=True,source="enc_rulefield1",many=True)
	FieldSecondary = FieldMappingSerializer(read_only=True,source="enc_rulefield2",many=True)


	class Meta:
		model = Ruleset
		fields = ("Model","RuleKey", "Operation","Field1","Field2","FieldPrimary","FieldSecondary",'exceptions')

class RuleModelSerializer(serializers.ModelSerializer):

	ruleset = RulesetSerializer(read_only=True,source="enc_ruleset",many=True)

	class Meta:
		model=RuleModel
		fields=("ModelName", "CreateDate", "ruleset")

