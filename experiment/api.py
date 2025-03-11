# experiment/api.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import EmotionFeedback, LEDPattern, Demographics, Signal
from .gesture_generator import GestureGenerator
import random

class EmotionFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for emotion feedback
    """
    queryset = EmotionFeedback.objects.all()

    def create(self, request):
        try:
            # Get demographics from session
            demographics_id = request.session.get('demographics_id')
            if not demographics_id:
                return Response(
                    {'error': 'No demographics found in session'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            demographics = get_object_or_404(Demographics, id=demographics_id)
            signal = get_object_or_404(Signal, id=request.data.get('signal_id'))

            # Validate valence and arousal
            valence = float(request.data.get('valence', 0))
            arousal = float(request.data.get('arousal', 0))
            
            if not (-1 <= valence <= 1) or not (-1 <= arousal <= 1):
                return Response(
                    {'error': 'Valence and arousal must be between -1 and 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create feedback
            feedback = EmotionFeedback.objects.create(
                demographics=demographics,
                signal=signal,
                valence=valence,
                arousal=arousal,
                notes=request.data.get('notes', '')
            )

            return Response({
                'id': feedback.id,
                'timestamp': feedback.timestamp,
                'message': 'Feedback recorded successfully'
            }, status=status.HTTP_201_CREATED)

        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid data format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LEDPatternViewSet(viewsets.ModelViewSet):
    """
    API endpoint for LED patterns
    """
    queryset = LEDPattern.objects.all()
    gesture_generator = GestureGenerator()

    @action(detail=False, methods=['post'])
    def generate(self, request):
        try:
            pattern_type = request.data.get('pattern_type')
            if not pattern_type:
                return Response(
                    {'error': 'Pattern type is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            parameters = request.data.get('parameters', {})
            
            # Generate pattern
            pattern_data = self.gesture_generator.generate_pattern(
                pattern_type,
                parameters
            )

            # Save pattern to database
            pattern = LEDPattern.objects.create(
                name=request.data.get('name', f'Generated {pattern_type.title()} Pattern'),
                pattern_type=pattern_type,
                parameters=pattern_data
            )

            return Response({
                'id': pattern.id,
                'pattern': pattern_data,
                'message': 'Pattern generated successfully'
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def random(self, request):
        try:
            # Generate random pattern
            pattern_type = random.choice(list(dict(LEDPattern.PATTERN_TYPES).keys()))
            parameters = {
                'color': self.gesture_generator.random_color(),
                'duration': 5000,  # 5 seconds
            }
            
            pattern_data = self.gesture_generator.generate_pattern(
                pattern_type,
                parameters
            )

            # Save pattern to database
            pattern = LEDPattern.objects.create(
                name=f'Random {pattern_type.title()} Pattern',
                pattern_type=pattern_type,
                parameters=pattern_data
            )

            return Response({
                'id': pattern.id,
                'pattern': pattern_data,
                'message': 'Random pattern generated successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 