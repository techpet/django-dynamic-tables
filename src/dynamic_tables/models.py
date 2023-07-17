from django.db import models


class Table(models.Model):
	"""
	Django table that stores dynamic table names and ids.

	This would be used as a table meta repository and should allow us to retrieve a table using its id
	"""
	
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=200)
	schema = models.JSONField(default=None)
