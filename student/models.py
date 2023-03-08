from django.db import models
from school.models import School


class Student(models.Model):
    
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    grade = models.CharField(max_length=10, null=True)
    school = models.ForeignKey(
        School, related_name="school", on_delete=models.CASCADE)

    def __str__(self):
        return self.username
