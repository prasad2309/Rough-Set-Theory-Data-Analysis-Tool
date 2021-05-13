from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class stability_index(models.Model):
	args = PickledObjectField()

class dates(models.Model):
	date = models.CharField(max_length=200, null=True)

class threshold(models.Model):
	value = models.FloatField(null=True, blank=True, default=None)

class last_outputs(models.Model):
	args = PickledObjectField()

class github(models.Model):
	link = models.CharField(max_length=500, null=True)
