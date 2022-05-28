from django.db import models


class JobTitles(models.Model):
    JobCode = models.CharField(max_length=40,primary_key=True)
    JobTitle = models.CharField(max_length=400,default="N/A")
    Description = models.TextField()

class DescGram(models.Model):
    JobCodeKey = models.ForeignKey(JobTitles, related_name="desc_encrypt",on_delete=models.CASCADE,default="N/A")
    GramKey = models.CharField(max_length=30,primary_key=True,default="NA")
    GramIndicator = models.CharField(max_length=20,default="NA")
    Text = models.TextField()
    Category = models.CharField(max_length=200,default="")
    TopicNum = models.IntegerField(default=0)
    Embedding1 = models.DecimalField(max_digits=8,decimal_places=6,default=0)
    Embedding2 = models.DecimalField(max_digits=8,decimal_places=6,default=0)
    Embedding3 = models.DecimalField(max_digits=8,decimal_places=6,default=0)
    
class RelatedDesc(models.Model):
    GramPrimary = models.ForeignKey(DescGram, related_name="relateddesc_encrypt",on_delete=models.CASCADE)
    GramRelated = models.CharField(max_length = 40)
