# experiment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
import csv
import json
from datetime import datetime
from .models import Experiment, Demographics, Signal, EmotionFeedback
from .gesture_generator import GestureGenerator

def welcome(request):
    # Clear only participant-specific session data
    participant_keys = [
        'demographics_data',
        'feedback_data',
        'completed_signals',
        'participant_name'
    ]
    for key in participant_keys:
        request.session.pop(key, None)
    
    # Get the active experiment or use the first one
    experiment = Experiment.objects.filter(is_active=True).first()
    if not experiment:
        experiment = Experiment.objects.first()
    
    if not experiment:
        return render(request, 'experiment/error.html', {'message': 'No experiments available.'})
    
    if request.method == 'POST':
        # Store demographics data in session instead of creating database record
        demographics_data = {
            'experiment_id': experiment.id,
            'gender': request.POST.get('gender'),
            'age_range': request.POST.get('age_range'),
            'education': request.POST.get('education'),
            'robot_experience': request.POST.get('robot_experience'),
            'nationality': request.POST.get('nationality'),
        }
        
        # Store the demographics data in the session
        request.session['demographics_data'] = demographics_data
        
        # Store the name in the session
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        request.session['participant_name'] = f"{first_name} {last_name}"
        
        return redirect('instructions')
    
    return render(request, 'experiment/welcome.html', {'experiment': experiment})

def instructions(request):
    # Get the name from session
    participant_name = request.session.get('participant_name', '')
    return render(request, 'experiment/instructions.html', {'participant_name': participant_name})

def experiment(request):
    # Check if demographics data exists in session
    demographics_data = request.session.get('demographics_data')
    if not demographics_data:
        return redirect('welcome')
    
    experiment = get_object_or_404(Experiment, id=demographics_data['experiment_id'])
    
    # Get all signals for this experiment
    signals = Signal.objects.filter(experiment=experiment)
    if not signals.exists():
        return render(request, 'experiment/error.html', {
            'message': 'No signals available for this experiment.'
        })
    
    # Get completed signals from session
    completed_signals = request.session.get('completed_signals', [])
    
    # Get next signal
    next_signal = signals.exclude(id__in=completed_signals).first()
    
    # Check if experiment is complete
    if not next_signal:
        return redirect('experiment_complete')
    
    context = {
        'experiment': experiment,
        'signal': next_signal,
        'progress': {
            'completed': len(completed_signals),
            'total': signals.count()
        }
    }
    
    return render(request, 'experiment/experiment.html', context)

def get_next_signal(request):
    """API endpoint to get the next signal for the participant."""
    demographics_data = request.session.get('demographics_data')
    if not demographics_data:
        return JsonResponse({'error': 'No active session'}, status=401)
    
    experiment = get_object_or_404(Experiment, id=demographics_data['experiment_id'])
    
    # Get all signals and completed signals
    signals = Signal.objects.filter(experiment=experiment)
    completed_signals = request.session.get('completed_signals', [])
    
    # Get next signal
    next_signal = signals.exclude(id__in=completed_signals).first()
    
    if not next_signal:
        return JsonResponse({
            'complete': True,
            'message': 'Experiment complete'
        })
    
    return JsonResponse({
        'signal_id': next_signal.id,
        'pattern': next_signal.pattern,
        'progress': {
            'completed': len(completed_signals),
            'total': signals.count()
        }
    })

@require_POST
def skip_signal(request):
    try:
        data = json.loads(request.body)
        signal_id = data.get('signal_id')
        response_time_ms = data.get('response_time_ms')
        
        # Get demographics data from session
        demographics_data = request.session.get('demographics_data')
        if not demographics_data:
            return JsonResponse({'error': 'No active session'}, status=401)
        
        # Store skip data in session
        feedback_data = request.session.get('feedback_data', [])
        feedback_data.append({
            'signal_id': signal_id,
            'valence': 0,
            'arousal': 0,
            'response_time_ms': response_time_ms,
            'notes': 'Skipped'
        })
        request.session['feedback_data'] = feedback_data
        
        # Add to completed signals
        completed_signals = request.session.get('completed_signals', [])
        completed_signals.append(signal_id)
        request.session['completed_signals'] = completed_signals
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def submit_feedback(request):
    try:
        data = json.loads(request.body)
        signal_id = data.get('signal_id')
        valence = data.get('valence')
        arousal = data.get('arousal')
        response_time_ms = data.get('response_time_ms')
        
        # Get demographics data from session
        demographics_data = request.session.get('demographics_data')
        if not demographics_data:
            return JsonResponse({'error': 'No active session'}, status=401)
        
        # Store feedback data in session
        feedback_data = request.session.get('feedback_data', [])
        feedback_data.append({
            'signal_id': signal_id,
            'valence': valence,
            'arousal': arousal,
            'response_time_ms': response_time_ms
        })
        request.session['feedback_data'] = feedback_data
        
        # Add to completed signals
        completed_signals = request.session.get('completed_signals', [])
        completed_signals.append(signal_id)
        request.session['completed_signals'] = completed_signals
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def export_data(request, experiment_id=None):
    """Export experiment data in CSV format."""
    # Get experiment
    if experiment_id:
        experiment = get_object_or_404(Experiment, id=experiment_id)
        feedbacks = EmotionFeedback.objects.filter(demographics__experiment=experiment)
    else:
        feedbacks = EmotionFeedback.objects.all()
        
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="experiment_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Experiment Name',
        'Participant ID',
        'Gender',
        'Age Range',
        'Education',
        'Robot Experience',
        'Nationality',
        'Signal Name',
        'Pattern Type',
        'Pattern Parameters',
        'Valence',
        'Arousal',
        'Response Time (ms)',
        'Notes'
    ])
    
    # Write data rows
    for feedback in feedbacks:
        pattern_data = json.loads(feedback.signal.pattern) if isinstance(feedback.signal.pattern, str) else feedback.signal.pattern
        writer.writerow([
            feedback.demographics.experiment.name,
            feedback.demographics.id,
            feedback.demographics.get_gender_display(),
            feedback.demographics.age_range,
            feedback.demographics.get_education_display(),
            feedback.demographics.get_robot_experience_display(),
            feedback.demographics.get_nationality_display(),
            feedback.signal.name,
            pattern_data.get('type', ''),
            json.dumps(pattern_data),
            feedback.valence,
            feedback.arousal,
            feedback.response_time_ms,
            feedback.notes
        ])
    
    return response

@staff_member_required
def experiment_statistics(request, experiment_id):
    """Get statistics for an experiment."""
    experiment = get_object_or_404(Experiment, id=experiment_id)
    
    # Get all feedback for this experiment
    feedbacks = EmotionFeedback.objects.filter(demographics__experiment=experiment)
    
    # Calculate statistics
    stats = {
        'total_participants': Demographics.objects.filter(experiment=experiment).count(),
        'total_feedbacks': feedbacks.count(),
        'average_valence': feedbacks.aggregate(Avg('valence'))['valence__avg'],
        'average_arousal': feedbacks.aggregate(Avg('arousal'))['arousal__avg'],
        'average_response_time': feedbacks.aggregate(Avg('response_time_ms'))['response_time_ms__avg'],
        'gender_distribution': dict(
            Demographics.objects.filter(experiment=experiment)
            .values_list('gender')
            .annotate(count=Count('gender'))
        ),
        'age_distribution': dict(
            Demographics.objects.filter(experiment=experiment)
            .values_list('age_range')
            .annotate(count=Count('age_range'))
        ),
        'pattern_distribution': dict(
            Signal.objects.filter(experiment=experiment)
            .values_list('pattern__type')
            .annotate(count=Count('pattern__type'))
        )
    }
    
    return JsonResponse(stats)

def experiment_complete(request):
    """Handle experiment completion and save all data to database."""
    # Get the demographics data from session
    demographics_data = request.session.get('demographics_data')
    feedback_data = request.session.get('feedback_data', [])
    
    if not demographics_data:
        return redirect('welcome')
    
    try:
        # Create demographics record
        experiment = get_object_or_404(Experiment, id=demographics_data['experiment_id'])
        demographics = Demographics.objects.create(
            experiment=experiment,
            gender=demographics_data['gender'],
            age_range=demographics_data['age_range'],
            education=demographics_data['education'],
            robot_experience=demographics_data['robot_experience'],
            nationality=demographics_data['nationality']
        )
        
        # Create all feedback records
        for feedback in feedback_data:
            signal = get_object_or_404(Signal, id=feedback['signal_id'])
            EmotionFeedback.objects.create(
                demographics=demographics,
                signal=signal,
                valence=feedback['valence'],
                arousal=feedback['arousal'],
                response_time_ms=feedback['response_time_ms'],
                notes=feedback.get('notes', '')
            )
        
        # Clear all session data
        request.session.pop('demographics_data', None)
        request.session.pop('feedback_data', None)
        request.session.pop('completed_signals', None)
        request.session.pop('participant_name', None)
        
        return render(request, 'experiment/complete.html', {
            'demographics': demographics,
            'experiment': experiment,
            'feedback_count': len(feedback_data)
        })
        
    except Exception as e:
        # If there's an error, redirect to welcome page
        for key in ['demographics_data', 'feedback_data', 'completed_signals', 'participant_name']:
            request.session.pop(key, None)
        return redirect('welcome')

@staff_member_required
def create_test_signals(request, experiment_id):
    """Create test signals for an experiment."""
    experiment = get_object_or_404(Experiment, id=experiment_id)
    gesture_generator = GestureGenerator()
    
    # Define test patterns
    test_patterns = [
        {
            'name': 'Calm Blue Wave',
            'pattern': gesture_generator.generate_pattern('wave', {
                'color': '#0066cc',
                'wave_length': 10,
                'speed': 0.5
            })
        },
        {
            'name': 'Excited Red Blink',
            'pattern': gesture_generator.generate_pattern('blink', {
                'color': '#ff3333',
                'frequency': 2
            })
        },
        {
            'name': 'Happy Yellow Pulse',
            'pattern': gesture_generator.generate_pattern('pulse', {
                'color': '#ffcc00',
                'pulse_speed': 1,
                'min_brightness': 20,
                'max_brightness': 100
            })
        },
        {
            'name': 'Peaceful Green Fade',
            'pattern': gesture_generator.generate_pattern('fade', {
                'start_color': '#004d00',
                'end_color': '#00ff00',
                'steps': 50
            })
        },
        {
            'name': 'Energetic Rainbow',
            'pattern': gesture_generator.generate_pattern('rainbow', {
                'speed': 1,
                'brightness': 100
            })
        },
        {
            'name': 'Calm Purple Solid',
            'pattern': gesture_generator.generate_pattern('solid', {
                'color': '#660099',
                'brightness': 80
            })
        }
    ]
    
    # Create signals
    created_count = 0
    for pattern in test_patterns:
        signal, created = Signal.objects.get_or_create(
            experiment=experiment,
            name=pattern['name'],
            defaults={'pattern': pattern['pattern']}
        )
        if created:
            created_count += 1
    
    return JsonResponse({
        'message': f'Created {created_count} test signals for experiment {experiment.name}',
        'total_signals': Signal.objects.filter(experiment=experiment).count()
    })