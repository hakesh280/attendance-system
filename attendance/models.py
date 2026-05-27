from django.db import models

class Student(models.Model):

    name = models.CharField(max_length=100)

    usn = models.CharField(max_length=20)

    department = models.CharField(max_length=50)

    semester = models.IntegerField()

    def __str__(self):
        return self.name


class Attendance(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    date = models.DateField()

    status = models.CharField(max_length=10)

    def __str__(self):
        return self.student.name