from django.db import models

class Student(models.Model):
    # This is our database table
    name = models.CharField(max_length=100)
    study_hours = models.FloatField()
    attendance = models.IntegerField()
    # This will store what the AI thinks (Pass/Fail)
    prediction = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name