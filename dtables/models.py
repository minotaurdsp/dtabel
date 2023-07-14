from django.db import models

class DynamicTable(models.Model):
    name = models.CharField(max_length=100)

class DynamicField(models.Model):
    dynamic_table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50)

    
