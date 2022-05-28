from rest_framework import serializers
from .models import *

class BasicQuerySerializer(serializers.ModelSerializer):
	class Meta:
		model = BasicQuery
		fields = "__all__"


class QueryModelSerializer(serializers.ModelSerializer):
	basicquery = BasicQuerySerializer(read_only=True,source="enc_basic",many=True)

	class Meta:
		model = QueryModel
		fields = ("ModelName","ChartType","Status","XFieldName","RuleModelName","AsofDate",
						"NPeriods","Period","basicquery")


