# experiment/gesture_generator.py
import random
import colorsys

class GestureGenerator:
    def __init__(self):
        self.default_duration = 5000  # Default duration in milliseconds
        self.default_num_leds = 8    # Default number of LEDs in strip

    def generate_pattern(self, pattern_type, parameters=None):
        """Generate LED pattern based on type and parameters."""
        if parameters is None:
            parameters = {}

        # Always enforce 8 LEDs
        parameters['num_leds'] = 8
        parameters['duration'] = parameters.get('duration', self.default_duration)

        pattern_functions = {
            'blink': self._generate_blink_pattern,
            'fade': self._generate_fade_pattern,
            'wave': self._generate_wave_pattern,
            'pulse': self._generate_pulse_pattern,
            'rainbow': self._generate_rainbow_pattern,
            'solid': self._generate_solid_pattern,
        }

        if pattern_type not in pattern_functions:
            raise ValueError(f"Unknown pattern type: {pattern_type}")

        pattern = pattern_functions[pattern_type](parameters['duration'], parameters['num_leds'], parameters)
        pattern['type'] = pattern_type  # Ensure type is always set
        return pattern

    def _generate_blink_pattern(self, duration, num_leds, parameters):
        """Generate a blinking pattern."""
        return {
            'type': 'blink',
            'color': parameters.get('color', '#FF0000'),
            'frequency': parameters.get('frequency', 2.0),
            'duty_cycle': parameters.get('duty_cycle', 0.4),
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_fade_pattern(self, duration, num_leds, parameters):
        """Generate a fading pattern."""
        return {
            'type': 'fade',
            'start_color': parameters.get('start_color', '#000000'),
            'end_color': parameters.get('end_color', '#FFFFFF'),
            'steps': parameters.get('steps', 20),
            'fade_type': parameters.get('fade_type', 'linear'),
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_wave_pattern(self, duration, num_leds, parameters):
        """Generate a wave pattern."""
        return {
            'type': 'wave',
            'color': parameters.get('color', '#0000FF'),
            'wave_length': parameters.get('wave_length', 4),
            'speed': parameters.get('speed', 1.0),
            'wave_type': parameters.get('wave_type', 'sine'),
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_pulse_pattern(self, duration, num_leds, parameters):
        """Generate a pulsing pattern."""
        return {
            'type': 'pulse',
            'color': parameters.get('color', '#FF0000'),
            'pulse_speed': parameters.get('pulse_speed', 1.0),
            'min_brightness': parameters.get('min_brightness', 5),
            'max_brightness': parameters.get('max_brightness', 100),
            'pulse_type': parameters.get('pulse_type', 'sine'),
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_rainbow_pattern(self, duration, num_leds, parameters):
        """Generate a rainbow pattern."""
        return {
            'type': 'rainbow',
            'speed': parameters.get('speed', 1.0),
            'brightness': parameters.get('brightness', 100),
            'saturation': parameters.get('saturation', 100),
            'pattern': parameters.get('pattern', 'cycle'),
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_solid_pattern(self, duration, num_leds, parameters):
        """Generate a solid color pattern."""
        return {
            'type': 'solid',
            'color': parameters.get('color', '#FFFFFF'),
            'brightness': parameters.get('brightness', 100),
            'pulse_subtle': parameters.get('pulse_subtle', False),
            'duration': duration,
            'num_leds': num_leds
        }

    @staticmethod
    def random_color():
        """Generate a random color in hex format."""
        r = random.random()
        g = random.random()
        b = random.random()
        return '#{:02x}{:02x}{:02x}'.format(
            int(r * 255),
            int(g * 255),
            int(b * 255)
        ) 