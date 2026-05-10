from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    study_hours = models.FloatField()
    attendance = models.IntegerField()
    prediction = models.CharField(max_length=20, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name
