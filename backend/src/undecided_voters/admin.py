from django.contrib import admin

from .models import WeeklyAnalysis, ScrapingRun, RawPost


@admin.register(WeeklyAnalysis)
class WeeklyAnalysisAdmin(admin.ModelAdmin):
    list_display = ("week_start", "total_posts_analyzed", "reasons")
    readonly_fields = ("week_start", "total_posts_analyzed", "reasons", "created_at")
    ordering = ("-week_start",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and isinstance(obj.reasons, str):
            # Handle the case where reasons is stored as a string
            try:
                import json
                obj.reasons = json.loads(obj.reasons)
            except json.JSONDecodeError:
                pass
        return form


@admin.register(ScrapingRun)
class ScrapingRunAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "status", "total_posts_scraped")
    readonly_fields = ("start_time", "end_time", "status", "total_posts_scraped", "error_message")
    ordering = ("-start_time",)


@admin.register(RawPost)
class RawPostAdmin(admin.ModelAdmin):
    list_display = ("source", "post_date", "author", "created_at")
    readonly_fields = ("scraping_run", "source", "content", "post_date", "author", "metadata", "created_at")
    ordering = ("-post_date",)
    list_filter = ("source", "post_date")
    search_fields = ("content", "author")
    
    
