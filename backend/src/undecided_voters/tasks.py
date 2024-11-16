# tasks.py
from datetime import datetime, timedelta
from typing import Optional

from celery import shared_task
from celery.schedules import crontab

from .models import SourceChoices
from .scraper import UndecidedVoterAnalyzer


@shared_task
def run_daily_scraping(source: str, from_date: str, to_date: str) -> None:
    """Run daily scraping task
    
    Args:
        source: Data source identifier
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
    """
    analyzer = UndecidedVoterAnalyzer()
    analyzer.run_scraping_sync(source=source, from_date=from_date, to_date=to_date)


@shared_task
def run_weekly_analysis(source: str, week_start: str) -> None:
    """Run weekly analysis task
    
    Args:
        source: Data source identifier
        week_start: Analysis start date in YYYY-MM-DD format
    """
    analyzer = UndecidedVoterAnalyzer()
    analyzer.analyze_week(week_start_date=week_start, source=source)
