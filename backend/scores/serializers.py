from rest_framework import serializers
from .models import Student, SubjectScore

class SubjectScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectScore
        fields = ['subject', 'score']

class StudentScoreSerializer(serializers.ModelSerializer):
    scores = SubjectScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ['sbd', 'scores']