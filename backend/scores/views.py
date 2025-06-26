from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q, Prefetch, F, Sum, FloatField, Value
from django.shortcuts import get_object_or_404
from .models import Student, SubjectScore
from .serializers import StudentScoreSerializer
from scores.utils.subjects import Subject
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class ScoreBySBDView(APIView):
    def get(self, request, sbd):
        # Prefetch all subject scores in one query
        student = get_object_or_404(Student.objects.prefetch_related("scores"), sbd=sbd)
        serializer = StudentScoreSerializer(student)
        return Response(serializer.data)

@method_decorator(cache_page(60 * 5), name='dispatch')
class ReportScoresView(APIView):
    def get(self, request):
        result = {}
        # Use one single DB query instead of one per filter
        for subject in Subject.all_keys():
            qs = SubjectScore.objects.filter(subject=subject).values('score')
            result[subject] = {
                ">=8": qs.filter(score__gte=8).count(),
                "6-8": qs.filter(score__lt=8, score__gte=6).count(),
                "4-6": qs.filter(score__lt=6, score__gte=4).count(),
                "<4": qs.filter(score__lt=4).count(),
            }
        return Response(result)

@method_decorator(cache_page(60 * 5), name='dispatch')
class Top10GroupAView(APIView):
    def get(self, request):
        group_a = ["toan", "vat_li", "hoa_hoc"]

        # Prefetch all subject scores to avoid multiple queries
        students = Student.objects.only("sbd").prefetch_related(
            Prefetch(
                "scores",
                queryset=SubjectScore.objects.filter(subject__in=group_a).only("subject", "score", "student")
            )
        )

        result = []
        for student in students:
            scores = {s.subject: s.score for s in student.scores.all()}
            if all(sub in scores for sub in group_a):
                total = sum(scores[sub] for sub in group_a)
                result.append({"sbd": student.sbd, "total": round(total, 2)})


        # Sort once, not in every iteration
        top10 = sorted(result, key=lambda x: x["total"], reverse=True)[:10]
        return Response(top10)
