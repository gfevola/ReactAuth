from rest_framework import serializers
from .models import FieldMapping


class FieldMappingSerializer(serializers.ModelSerializer):
	class Meta:
		model = FieldMapping
		fields = "__all__"
