from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Experiment, Demographics, Signal, EmotionFeedback, LEDPattern
import csv
from django.http import HttpResponse
import json

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'participant_count', 'signal_count', 'action_buttons')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    actions = ['activate_experiments', 'deactivate_experiments', 'download_data']

    def activate_experiments(self, request, queryset):
        queryset.update(is_active=True)
    activate_experiments.short_description = "Activate selected experiments"

    def deactivate_experiments(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_experiments.short_description = "Deactivate selected experiments"

    def download_data(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="experiment_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Description', 'Is Active'])
        for experiment in queryset:
            writer.writerow([experiment.name, experiment.description, experiment.is_active])
        return response
    download_data.short_description = "Download selected experiments as CSV"

    def participant_count(self, obj):
        return Demographics.objects.filter(experiment=obj).count()
    participant_count.short_description = 'Participants'

    def signal_count(self, obj):
        return Signal.objects.filter(experiment=obj).count()
    signal_count.short_description = 'Signals'

    def action_buttons(self, obj):
        export_url = reverse('export_experiment_data', args=[obj.id])
        stats_url = reverse('experiment_statistics', args=[obj.id])
        test_signals_url = reverse('create_test_signals', args=[obj.id])
        
        return format_html(
            '<a class="button" href="{}">Export Data</a>&nbsp;'
            '<a class="button" href="{}">View Statistics</a>&nbsp;'
            '<a class="button" href="{}">Create Test Signals</a>',
            export_url, stats_url, test_signals_url
        )
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'pattern_type', 'feedback_count')
    list_filter = ('experiment',)
    search_fields = ('name', 'experiment__name')

    def pattern_type(self, obj):
        if isinstance(obj.pattern, dict):
            return obj.pattern.get('type', 'Unknown')
        try:
            pattern_data = json.loads(obj.pattern)
            return pattern_data.get('type', 'Unknown')
        except (json.JSONDecodeError, AttributeError, TypeError):
            return 'Unknown'
    pattern_type.short_description = 'Pattern Type'

    def feedback_count(self, obj):
        return obj.emotion_feedbacks.count()
    feedback_count.short_description = 'Feedback Count'

@admin.register(Demographics)
class DemographicsAdmin(admin.ModelAdmin):
    list_display = ('id', 'experiment', 'gender', 'age_range', 'education', 'robot_experience','nationality', 'created_at')
    list_filter = ('experiment', 'gender', 'age_range', 'education', 'robot_experience','nationality')
    search_fields = ('id', 'experiment__name')
    readonly_fields = ('created_at',)

@admin.register(EmotionFeedback)
class EmotionFeedbackAdmin(admin.ModelAdmin):
    list_display = ('demographics', 'signal', 'valence', 'arousal', 'response_time_ms', 'timestamp')
    list_filter = ('demographics__experiment', 'timestamp')
    search_fields = ('demographics__id', 'signal__name')
    readonly_fields = ('timestamp', 'response_time_ms')

@admin.register(LEDPattern)
class LEDPatternAdmin(admin.ModelAdmin):
    list_display = ('name', 'pattern_type', 'is_active', 'created_at')
    list_filter = ('pattern_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
