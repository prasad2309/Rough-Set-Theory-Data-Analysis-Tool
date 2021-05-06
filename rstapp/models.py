from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class stability_index(models.Model):
	args = PickledObjectField()

class dates(models.Model):
	filename = models.CharField(max_length=200, null=True)
	date = models.CharField(max_length=200, null=True)


class threshold(models.Model):
	value = models.FloatField(null=True, blank=True, default=None)

class last_outputs(models.Model):
	args = PickledObjectField()