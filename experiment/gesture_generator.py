# experiment/gesture_generator.py
import random
import colorsys

class GestureGenerator:
    def __init__(self):
        self.default_duration = 5000  # Default duration in milliseconds
        self.default_num_leds = 30    # Default number of LEDs in strip

    def generate_pattern(self, pattern_type, parameters=None):
        """Generate LED pattern based on type and parameters."""
        if parameters is None:
            parameters = {}

        # Set default parameters if not provided
        duration = parameters.get('duration', self.default_duration)
        num_leds = parameters.get('num_leds', self.default_num_leds)

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

        return pattern_functions[pattern_type](duration, num_leds, parameters)

    def _generate_blink_pattern(self, duration, num_leds, parameters):
        """Generate a blinking pattern."""
        color = parameters.get('color', '#FF0000')  # Default to red
        frequency = parameters.get('frequency', 2)   # Blinks per second

        return {
            'type': 'blink',
            'color': color,
            'frequency': frequency,
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_fade_pattern(self, duration, num_leds, parameters):
        """Generate a fading pattern."""
        start_color = parameters.get('start_color', '#000000')
        end_color = parameters.get('end_color', '#FFFFFF')
        steps = parameters.get('steps', 50)

        return {
            'type': 'fade',
            'start_color': start_color,
            'end_color': end_color,
            'steps': steps,
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_wave_pattern(self, duration, num_leds, parameters):
        """Generate a wave pattern."""
        color = parameters.get('color', '#0000FF')  # Default to blue
        wave_length = parameters.get('wave_length', num_leds // 3)
        speed = parameters.get('speed', 1)  # Waves per second

        return {
            'type': 'wave',
            'color': color,
            'wave_length': wave_length,
            'speed': speed,
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_pulse_pattern(self, duration, num_leds, parameters):
        """Generate a pulsing pattern."""
        color = parameters.get('color', '#FF0000')  # Default to red
        pulse_speed = parameters.get('pulse_speed', 1)  # Pulses per second
        min_brightness = parameters.get('min_brightness', 0)
        max_brightness = parameters.get('max_brightness', 100)

        return {
            'type': 'pulse',
            'color': color,
            'pulse_speed': pulse_speed,
            'min_brightness': min_brightness,
            'max_brightness': max_brightness,
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_rainbow_pattern(self, duration, num_leds, parameters):
        """Generate a rainbow pattern."""
        speed = parameters.get('speed', 1)  # Rotations per second
        brightness = parameters.get('brightness', 100)

        return {
            'type': 'rainbow',
            'speed': speed,
            'brightness': brightness,
            'duration': duration,
            'num_leds': num_leds
        }

    def _generate_solid_pattern(self, duration, num_leds, parameters):
        """Generate a solid color pattern."""
        color = parameters.get('color', '#FFFFFF')  # Default to white
        brightness = parameters.get('brightness', 100)

        return {
            'type': 'solid',
            'color': color,
            'brightness': brightness,
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