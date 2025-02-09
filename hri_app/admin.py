from django.contrib import admin
from .models import Feedback
from django.http import HttpResponse
import csv


# Custom admin action to download feedback as CSV
def download_feedback_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feedback.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'User Name', 'Animation Type', 'Rating'])  # Added 'ID'
    
    # Write data rows
    for feedback in queryset:
        writer.writerow([feedback.id, feedback.user_name, feedback.animation_type, feedback.rating])
    
    return response

download_feedback_as_csv.short_description = "Download selected feedback as CSV"

# Customize the Feedback admin interface
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'animation_type', 'rating')  # Added 'id'
    list_filter = ('animation_type', 'rating')  # Filters for the admin panel
    search_fields = ('user_name',)  # Search functionality (no comments field anymore)
    actions = [download_feedback_as_csv]  # Add the custom action

    # Count the number of feedback entries in the admin page
    def changelist_view(self, request, extra_context=None):
        # Add count to the context
        extra_context = extra_context or {}
        extra_context['feedback_count'] = Feedback.objects.count()
        return super().changelist_view(request, extra_context=extra_context)

# Register the Feedback model with the custom admin class
admin.site.register(Feedback, FeedbackAdmin)
