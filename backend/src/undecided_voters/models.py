from django.db import models


class SourceChoices:
    TWITTER = "twitter"
    NEWS_API = "newsapi"
    ALL = "all"

    CHOICES = [
        (TWITTER, "Twitter"),
        (NEWS_API, "News API"),
        (ALL, "All Sources"),
    ]


class ScrapingRun(models.Model):
    """Track each scraping session"""

    source = models.CharField(
        max_length=20,
        choices=SourceChoices.CHOICES,
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    date_range_start = models.DateTimeField(null=True)
    date_range_end = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("RUNNING", "Running"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ],
    )
    total_posts_scraped = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)


class RawPost(models.Model):
    """Store raw scraped posts"""

    scraping_run = models.ForeignKey(ScrapingRun, on_delete=models.CASCADE)
    source = models.CharField(max_length=50, choices=SourceChoices.CHOICES)
    content = models.TextField()
    post_date = models.DateTimeField()
    author = models.CharField(max_length=255, null=True)
    metadata = models.JSONField(default=dict)  # likes, retweets, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    publisher = models.CharField(
        max_length=255, null=True, blank=True
    )  # CNN, BBC, etc.


class WeeklyAnalysis(models.Model):
    """Store weekly analysis results"""

    source = models.CharField(
        max_length=20,
        choices=SourceChoices.CHOICES,
    )
    week_start = models.DateField()
    week_end = models.DateField()
    total_posts_analyzed = models.IntegerField()

    # Main reasons stored as JSON with percentages
    reasons = models.JSONField()  # e.g., {"economy": 45, "healthcare": 30}

    # Store full OpenAI analysis
    detailed_analysis = models.JSONField()

    # Top quotes/examples for each reason
    supporting_evidence = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["week_start", "week_end", "source"]
