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
        student = get_object_or_404(Student.objects.prefetch_related("scores"), sbd=sbd)
        serializer = StudentScoreSerializer(student)
        return Response(serializer.data)

@method_decorator(cache_page(60 * 5), name='dispatch')
class ReportScoresView(APIView):
    def get(self, request):
        result = {}
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

        # Get students who have all 3 subjects
        students = (
            Student.objects.annotate(
                toan_score=Sum('scores__score', filter=Q(scores__subject='toan')),
                vat_li_score=Sum('scores__score', filter=Q(scores__subject='vat_li')),
                hoa_hoc_score=Sum('scores__score', filter=Q(scores__subject='hoa_hoc')),
                subject_count=Count('scores__subject', filter=Q(scores__subject__in=group_a), distinct=True),
            )
            .filter(subject_count=3)  # only those who have all 3
            .annotate(
                total_score=F('toan_score') + F('vat_li_score') + F('hoa_hoc_score')
            )
            .values(
                'sbd', 'toan_score', 'vat_li_score', 'hoa_hoc_score', 'total_score'
            )
            .order_by('-total_score')[:10]
        )

        # Format response
        result = [
            {
                "sbd": s["sbd"],
                "toan": s["toan_score"],
                "vat_li": s["vat_li_score"],
                "hoa_hoc": s["hoa_hoc_score"],
                "total": s["total_score"], 
            }
            for s in students
        ]

        return Response(result)
