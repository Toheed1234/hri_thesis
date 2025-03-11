# experiment/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

router = DefaultRouter()
router.register(r'feedback', api.EmotionFeedbackViewSet, basename='feedback')
router.register(r'patterns', api.LEDPatternViewSet, basename='patterns')

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('instructions/', views.instructions, name='instructions'),  
    path('experiment/', views.experiment, name='experiment'),
    path('experiment/next-signal/', views.get_next_signal, name='next-signal'),
    path('experiment/complete/', views.experiment_complete, name='complete'),
    path('experiment/skip-signal/', views.skip_signal, name='skip-signal'),
    path('experiment/submit-feedback/', views.submit_feedback, name='submit-feedback'),
    path('api/', include(router.urls)),
    
    # Data export URLs
    path('export/', views.export_data, name='export_all_data'),
    path('export/<int:experiment_id>/', views.export_data, name='export_experiment_data'),
    path('statistics/<int:experiment_id>/', views.experiment_statistics, name='experiment_statistics'),
    # Test data URLs
    path('create-test-signals/<int:experiment_id>/', views.create_test_signals, name='create_test_signals'),
]