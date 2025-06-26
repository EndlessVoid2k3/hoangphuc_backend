from django.db import models

class Student(models.Model):
    sbd = models.CharField(max_length=10, unique=True, db_index=True)

    def __str__(self):
        return self.sbd

class SubjectScore(models.Model):
    student = models.ForeignKey(Student, related_name='scores', on_delete=models.CASCADE)
    subject = models.CharField(max_length=20, db_index=True)
    score = models.FloatField()

    def __str__(self):
        return f"{self.student.sbd} - {self.subject}: {self.score}"