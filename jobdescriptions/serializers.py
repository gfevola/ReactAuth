from rest_framework import serializers
from .models import JobTitles, DescGram, RelatedDesc


class RelatedDescSerializer(serializers.ModelSerializer):

	class Meta:
		model = RelatedDesc
		fields = "__all__"


class DescGramSerializer(serializers.ModelSerializer):

	pairs = RelatedDescSerializer(read_only=True,source="relateddesc_encrypt",many=True)

	class Meta:
		model = DescGram
		fields = ("JobCodeKey","GramKey","GramIndicator","Text","Category","TopicNum",
				 "Embedding1", "Embedding2", "Embedding3", "pairs")

             
class JobTitlesSerializer(serializers.ModelSerializer):

	grams = DescGramSerializer(read_only=True,source="desc_encrypt",many=True)

	class Meta:
		model = JobTitles
		fields = ("JobCode","JobTitle","Description","grams")
