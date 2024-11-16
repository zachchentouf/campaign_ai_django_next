from rest_framework import serializers

from .models import WeeklyAnalysis


class WeeklyAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyAnalysis
        fields = "__all__"
