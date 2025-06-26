from django.urls import path
from .views import ScoreBySBDView, ReportScoresView, Top10GroupAView

urlpatterns = [
    path("api/score/<str:sbd>/", ScoreBySBDView.as_view(), name="score-by-sbd"),
    path("api/report/", ReportScoresView.as_view(), name="report-scores"),
    path("api/top10/", Top10GroupAView.as_view(), name="top10-group-a"),
]