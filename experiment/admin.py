from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.contrib import messages
from django.template.response import TemplateResponse
from .models import Experiment, Demographics, Signal, EmotionFeedback, LEDPattern
import csv
from django.http import HttpResponse, JsonResponse
import json

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'participant_count', 'signal_count', 'action_buttons')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    actions = ['activate_experiments', 'deactivate_experiments', 'download_data']
    change_list_template = 'admin/experiment/experiment_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate-patterns/<int:experiment_id>/',
                self.admin_site.admin_view(self.generate_patterns_view),
                name='experiment_experiment_generate_patterns',
            ),
            path(
                'evolve-patterns/<int:experiment_id>/',
                self.admin_site.admin_view(self.evolve_patterns_view),
                name='experiment_experiment_evolve_patterns',
            ),
        ]
        return custom_urls + urls

    def generate_patterns_view(self, request, experiment_id):
        """View for generating patterns for a specific emotion"""
        experiment = self.get_object(request, experiment_id)
        
        if request.method == 'POST':
            valence = float(request.POST.get('valence', 0))
            arousal = float(request.POST.get('arousal', 0))
            
            try:
                from .views import create_initial_signals
                request.target_emotion = {'valence': valence, 'arousal': arousal}
                response = create_initial_signals(request, experiment_id)
                
                if response.status_code == 200:
                    data = json.loads(response.content)
                    messages.success(request, f"Generated {len(data['signals'])} patterns for emotion (valence: {valence}, arousal: {arousal})")
                    return JsonResponse(data)
                else:
                    messages.error(request, "Error generating patterns")
                    return JsonResponse({'error': 'Failed to generate patterns'}, status=400)
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
            
        context = {
            'title': 'Generate Emotion Patterns',
            'experiment': experiment,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/experiment/generate_patterns.html', context)

    def evolve_patterns_view(self, request, experiment_id):
        """View for evolving patterns based on feedback"""
        experiment = self.get_object(request, experiment_id)
        
        try:
            from .views import generate_evolved_signals
            response = generate_evolved_signals(request, experiment_id)
            
            if response.status_code == 200:
                data = json.loads(response.content)
                messages.success(request, f"Successfully evolved patterns: {data.get('message', '')}")
                return JsonResponse(data)
            else:
                messages.error(request, "Error evolving patterns")
                return JsonResponse({'error': 'Failed to evolve patterns'}, status=400)
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def action_buttons(self, obj):
        export_url = reverse('export_experiment_data', args=[obj.id])
        stats_url = reverse('experiment_statistics', args=[obj.id])
        generate_url = reverse('admin:experiment_experiment_generate_patterns', args=[obj.id])
        evolve_url = reverse('admin:experiment_experiment_evolve_patterns', args=[obj.id])
        
        return format_html(
            '<a class="button" href="{}">Export Data</a>&nbsp;'
            '<a class="button" href="{}">View Statistics</a>&nbsp;'
            '<a class="button" href="{}">Generate Patterns</a>&nbsp;'
            '<a class="button" href="{}">Evolve Patterns</a>',
            export_url, stats_url, generate_url, evolve_url
        )
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

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
        writer.writerow(['Experiment', 'Signal', 'Valence', 'Arousal', 'Response Time'])
        
        for experiment in queryset:
            feedback = EmotionFeedback.objects.filter(demographics__experiment=experiment)
            for fb in feedback:
                writer.writerow([
                    experiment.name,
                    fb.signal.name,
                    fb.valence,
                    fb.arousal,
                    fb.response_time_ms
                ])
        return response
    download_data.short_description = "Download experiment data"

    def participant_count(self, obj):
        return Demographics.objects.filter(experiment=obj).count()
    participant_count.short_description = 'Participants'

    def signal_count(self, obj):
        return Signal.objects.filter(experiment=obj).count()
    signal_count.short_description = 'Signals'

@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'pattern_type', 'feedback_count')
    list_filter = ('experiment',)
    search_fields = ('name', 'experiment__name')

    def pattern_type(self, obj):
        try:
            pattern_data = obj.pattern
            return pattern_data.get('pattern_type', '-')
        except (AttributeError, KeyError):
            return '-'
    pattern_type.short_description = 'Pattern Type'

    def feedback_count(self, obj):
        return EmotionFeedback.objects.filter(signal=obj).count()
    feedback_count.short_description = 'Feedback Count'

@admin.register(Demographics)
class DemographicsAdmin(admin.ModelAdmin):
    list_display = ('id', 'experiment', 'gender', 'age_range', 'education', 'robot_experience', 'nationality', 'created_at')
    list_filter = ('experiment', 'gender', 'age_range', 'education', 'robot_experience', 'nationality')
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
