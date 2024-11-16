# views.py
from datetime import datetime, timedelta
from typing import Optional
from asgiref.sync import async_to_sync
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ScrapingRun, SourceChoices, WeeklyAnalysis
from .scraper import UndecidedVoterAnalyzer
from .serializers import WeeklyAnalysisSerializer
from .tasks import run_daily_scraping, run_weekly_analysis


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeeklyAnalysis.objects.all()
    serializer_class = WeeklyAnalysisSerializer

    @action(detail=False, methods=["post"])
    def trigger_scraping(self, request):
        """Manual trigger for scraping undecided voter posts"""
        try:
            from_date: str = request.query_params.get("from_date", "1970-01-01")
            to_date: str = request.query_params.get("to_date", "2040-01-01")
            source: str = request.query_params.get("source", "all")
            
            try:
                datetime.strptime(from_date, "%Y-%m-%d")
                datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate source
            if source not in dict(SourceChoices.CHOICES):
                return Response(
                    {
                        "error": f"Invalid source. Must be one of: {', '.join(dict(SourceChoices.CHOICES).keys())}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            run_daily_scraping.delay(
                source=source, from_date=from_date, to_date=to_date
            )

            return Response(
                {"status": f"Scraping triggered successfully for source: {source}"},
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as e:
            import traceback

            return Response(
                {
                    "status": "Failed to trigger scraping",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def trigger_analysis(self, request):
        """Manual trigger for analysis"""
        try:
            default_date = (datetime.now().date() - timedelta(days=7)).isoformat()
            week_start: str = request.query_params.get("week_start", default_date)
            
            # Validate date format
            try:
                datetime.strptime(week_start, "%Y-%m-%d")
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            source: str = request.query_params.get("source", "all")

            # Validate source
            if source not in dict(SourceChoices.CHOICES):
                return Response(
                    {
                        "error": f"Invalid source. Must be one of: {', '.join(dict(SourceChoices.CHOICES).keys())}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            run_weekly_analysis.delay(source=source, week_start=week_start)
            return Response(
                {"status": f"Analysis triggered successfully for source: {source}"},
                status=202,
            )
        except Exception as e:
            return Response(
                {"status": "Failed to trigger analysis", "error": str(e)}, status=500
            )

    @action(detail=False, methods=["get"])
    def trends(self, request):
        """Get trending reasons over time"""
        source = request.query_params.get("source", "all")
        weeks = self.get_queryset().filter(source=source).order_by("-week_start")[:10]
        trends = []

        for week in weeks:
            trends.append(
                {
                    "week": week.week_start,
                    "source": week.source,
                    "reasons": week.reasons,
                    "total_posts": week.total_posts_analyzed,
                }
            )

        return Response(trends)