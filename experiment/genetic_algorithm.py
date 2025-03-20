import random
import numpy as np
import colorsys
from typing import List, Dict, Tuple
from .models import LEDPattern, EmotionFeedback
from .gesture_generator import GestureGenerator

class LEDPatternGeneticAlgorithm:
    def __init__(self, population_size: int = 8, mutation_rate: float = 0.2):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.gesture_generator = GestureGenerator()
        self.generation = 0
        self.learning_history = []
        self.successful_colors = {}  # Track successful colors for each pattern type
        
    def _create_initial_population(self, target_emotion: Tuple[float, float]) -> List[Dict]:
        """Create initial population focused on a specific target emotion."""
        population = []
        valence, arousal = target_emotion
        
        # Allow all pattern types for any emotion
        pattern_types = ['pulse', 'wave', 'blink', 'fade', 'solid']
        
        # Ensure we have enough pattern types
        while len(pattern_types) < self.population_size:
            pattern_types.extend(pattern_types)
        
        # Randomly select different pattern types for each member
        selected_types = random.sample(pattern_types, self.population_size)
                
        # Generate patterns with focused parameters
        for pattern_type in selected_types:
            # Generate different parameters for each pattern
            random_seed = random.randint(0, 10000)  # Different seed for each pattern
            random.seed(random_seed)
            
            parameters = self._generate_emotion_based_parameters(pattern_type, target_emotion)
            pattern = self.gesture_generator.generate_pattern(pattern_type, parameters)
            pattern['target_emotion'] = target_emotion
            pattern['generation'] = self.generation
            population.append(pattern)
            
        # Reset random seed
        random.seed()
            
        return population
    
    def _generate_emotion_based_parameters(self, pattern_type: str, target_emotion: Tuple[float, float]) -> Dict:
        """Generate parameters based on target emotion with randomized colors."""
        valence, arousal = target_emotion
        
        # Base parameters with reduced LED count
        params = {
            'duration': 5000,
            'num_leds': 8  # Reduced from 30 to 8 LEDs
        }
        
        # Define the four basic colors in HSV format
        basic_colors = {
            'red': (0.0, 1.0, 1.0),    # Pure red
            'green': (0.33, 1.0, 1.0),  # Pure green
            'yellow': (0.17, 1.0, 1.0), # Pure yellow
            'blue': (0.67, 1.0, 1.0)    # Pure blue
        }
        
        # Randomly select one of the four colors
        color_name = random.choice(list(basic_colors.keys()))
        hue, saturation, value = basic_colors[color_name]
        
        # Adjust brightness based on arousal
        value = 0.3 + (abs(arousal) * 0.7)  # 0.3 to 1.0
        
        # Convert HSV to RGB and then to hex color
        rgb = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, saturation, value))
        color = '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        # Pattern-specific parameters adjusted for 8 LEDs
        if pattern_type == 'blink':
            # Higher frequency for high arousal
            base_frequency = 2.0
            frequency = base_frequency + (abs(arousal) * 2.5)
            params.update({
                'color': color,
                'frequency': frequency,
                'duty_cycle': 0.4
            })
        elif pattern_type == 'fade':
            # Slower transitions for low arousal
            steps = int(20 * (1 - abs(arousal)))
            params.update({
                'start_color': '#000000',
                'end_color': color,
                'steps': steps,
                'fade_type': 'sine'
            })
        elif pattern_type == 'wave':
            # Wave parameters based on arousal
            wave_length = int(4 * (1 - abs(arousal)))
            speed = 0.3 + (abs(arousal) * 1.7)
            params.update({
                'color': color,
                'wave_length': wave_length,
                'speed': speed,
                'wave_type': 'sine'
            })
        elif pattern_type == 'pulse':
            # Pulse speed based on arousal
            pulse_speed = 1.0 + (abs(arousal) * 2.0)
            params.update({
                'color': color,
                'pulse_speed': pulse_speed,
                'min_brightness': 20,
                'max_brightness': 95,
                'pulse_type': 'sine'
            })
        elif pattern_type == 'solid':
            params.update({
                'color': color,
                'brightness': int(50 + (abs(arousal) * 50)),
                'pulse_subtle': abs(arousal) > 0.3
            })
            
        return params
    
    def _calculate_fitness(self, pattern: Dict, feedback: List[EmotionFeedback], 
                         target_emotion: Tuple[float, float]) -> float:
        """Calculate fitness based on emotional match and feedback."""
        try:
            if not feedback:
                return 0.0
            
            # Calculate average emotional response
            avg_valence = sum(f.valence for f in feedback) / len(feedback)
            avg_arousal = sum(f.arousal for f in feedback) / len(feedback)
            
            # Calculate emotional match (normalized distance to target)
            valence_match = 1 - abs(avg_valence - target_emotion[0])
            arousal_match = 1 - abs(avg_arousal - target_emotion[1])
            
            # Calculate emotional match score
            emotional_match = (valence_match + arousal_match) / 2
            
            # Calculate feedback score (weighted average)
            feedback_score = sum(f.feedback for f in feedback) / len(feedback)
            
            # Stronger penalty for incorrect emotional direction
            direction_penalty = 0.0
            if (avg_valence > 0 and target_emotion[0] < 0) or (avg_valence < 0 and target_emotion[0] > 0):
                direction_penalty += 0.7  # Increased penalty for wrong valence direction
            if (avg_arousal > 0 and target_emotion[1] < 0) or (avg_arousal < 0 and target_emotion[1] > 0):
                direction_penalty += 0.7  # Increased penalty for wrong arousal direction
            
            # Calculate final fitness with balanced weights
            fitness = (0.5 * emotional_match + 0.5 * feedback_score) * (1 - direction_penalty)
            
            # Additional penalty for very poor emotional match
            if emotional_match < 0.4:  # Increased threshold
                fitness *= 0.3  # Stronger penalty (70% reduction)
            
            # Additional boost for patterns that excel in both metrics
            if emotional_match > 0.7 and feedback_score > 0.7:
                fitness *= 1.3  # Increased boost (30% boost)
            
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            print(f"Error calculating fitness: {str(e)}")
            return 0.0

    def evolve(self, current_population: List[Dict], feedback: List[EmotionFeedback], 
              target_emotion: Tuple[float, float]) -> Tuple[List[Dict], Dict]:
        """Evolve patterns with improved learning from feedback and maintained diversity."""
        try:
            self.generation += 1
            
            # If no current population or feedback, create initial one
            if not current_population or not feedback:
                return self._create_initial_population(target_emotion), {
                    'generation': self.generation,
                    'average_fitness': 0,
                    'best_fitness': 0,
                    'target_emotion': target_emotion,
                    'population_size': self.population_size
                }
            
            # Calculate fitness for current population
            fitness_scores = {}
            for i, pattern in enumerate(current_population):
                fitness_scores[i] = self._calculate_fitness(pattern, feedback, target_emotion)
            
            # Track learning progress
            avg_fitness = sum(fitness_scores.values()) / len(fitness_scores)
            best_fitness = max(fitness_scores.values())
            best_pattern_index = max(fitness_scores.items(), key=lambda x: x[1])[0]
            
            # Update successful colors based on current generation
            for i, pattern in enumerate(current_population):
                pattern_type = pattern['type']
                if fitness_scores[i] >= 0.6:  # Increased threshold for successful patterns
                    if pattern_type not in self.successful_colors:
                        self.successful_colors[pattern_type] = []
                    # Store color based on pattern type
                    if pattern_type == 'fade':
                        color_to_store = pattern['end_color']
                    else:
                        color_to_store = pattern['color']
                    self.successful_colors[pattern_type].append(color_to_store)
            
            learning_stats = {
                'generation': self.generation,
                'average_fitness': avg_fitness,
                'best_fitness': best_fitness,
                'target_emotion': target_emotion,
                'population_size': len(current_population)
            }
            self.learning_history.append(learning_stats)
            
            # Sort patterns by fitness
            sorted_patterns = sorted(
                [(i, pattern) for i, pattern in enumerate(current_population)],
                key=lambda x: fitness_scores[x[0]],
                reverse=True
            )
            
            new_population = []
            used_types = set()
            
            # Increased minimum fitness threshold
            min_fitness_threshold = 0.6  # Increased from 0.5
            
            # Keep only the very best patterns
            if fitness_scores[best_pattern_index] >= min_fitness_threshold:
                new_population.append(current_population[best_pattern_index].copy())
                used_types.add(current_population[best_pattern_index]['type'])
            
            # Add other good patterns with different types (more selective)
            for _, pattern in sorted_patterns:
                if (len(new_population) < 2 and 
                    pattern['type'] not in used_types and 
                    fitness_scores[_] >= min_fitness_threshold):
                    new_population.append(pattern.copy())
                    used_types.add(pattern['type'])
            
            # Fill remaining slots with new patterns
            while len(new_population) < self.population_size:
                # Determine available pattern types
                available_types = []
                for pattern_type in ['blink', 'pulse', 'wave', 'fade', 'solid']:
                    count = sum(1 for p in new_population if p['type'] == pattern_type)
                    if count < 2:  # Allow max 2 of each type
                        available_types.append(pattern_type)
                
                if not available_types:  # Fallback if no types available
                    available_types = ['blink', 'pulse', 'wave', 'fade', 'solid']
                
                # Select pattern type randomly from available types
                new_type = random.choice(available_types)
                
                # Generate new pattern with selected type
                new_pattern = self._generate_emotion_based_parameters(new_type, target_emotion)
                
                # Stronger bias towards successful colors
                if new_type in self.successful_colors and self.successful_colors[new_type]:
                    successful_colors = self.successful_colors[new_type]
                    # Use the most recent successful color with 90% probability
                    if random.random() < 0.9:
                        if new_type == 'fade':
                            new_pattern['start_color'] = '#000000'
                            new_pattern['end_color'] = successful_colors[-1]
                        else:
                            new_pattern['color'] = successful_colors[-1]
                
                new_pattern['type'] = new_type
                new_pattern['generation'] = self.generation
                new_pattern['target_emotion'] = target_emotion
                
                # Add to population
                new_population.append(new_pattern)
                used_types.add(new_type)
            
            return new_population, learning_stats
            
        except Exception as e:
            print(f"Error in evolution: {str(e)}")
            # If evolution fails, create a new initial population
            return self._create_initial_population(target_emotion), {
                'generation': self.generation,
                'error': str(e),
                'target_emotion': target_emotion,
                'population_size': self.population_size
            }
        
    def _tournament_select(self, sorted_patterns: List[Tuple[int, Dict]], fitness_scores: Dict[int, float]) -> Dict:
        """Select a pattern using tournament selection."""
        tournament_size = 3
        tournament = random.sample(sorted_patterns, min(tournament_size, len(sorted_patterns)))
        return max(tournament, key=lambda x: fitness_scores[x[0]])[1]
        
    def _crossover(self, parent1: Dict, parent2: Dict, target_emotion: Tuple[float, float]) -> Dict:
        """Create a new pattern by combining parameters from two parents."""
        try:
            child = parent1.copy()
            
            # Randomly choose which parameters to inherit from each parent
            if parent1['type'] == parent2['type']:
                for key in parent1.keys():
                    if key in ['type', 'target_emotion', 'generation']:
                        continue
                    
                    # 50% chance to inherit from each parent
                    if random.random() < 0.5 and key in parent2:
                        child[key] = parent2[key]
            else:
                # If different types, generate new parameters based on the chosen type
                new_params = self._generate_emotion_based_parameters(child['type'], target_emotion)
                child.update(new_params)
            
            # Ensure required parameters are present
            base_params = self._generate_emotion_based_parameters(child['type'], target_emotion)
            for key, value in base_params.items():
                if key not in child:
                    child[key] = value
            
            return child
            
        except Exception as e:
            print(f"Error in crossover: {str(e)}")
            # If crossover fails, return a fresh pattern
            return self._generate_emotion_based_parameters(parent1['type'], target_emotion)

    def _mutate(self, pattern: Dict) -> Dict:
        """Mutate pattern parameters with clear emotional intent."""
        try:
            mutated = pattern.copy()
            target_emotion = pattern.get('target_emotion', (0, 0))
            
            if random.random() < self.mutation_rate:
                # Get new parameters based on target emotion
                new_params = self._generate_emotion_based_parameters(pattern['type'], target_emotion)
                
                # Blend between current and new parameters
                blend_factor = random.uniform(0.3, 0.7)
                
                # Always ensure basic parameters exist
                mutated['num_leds'] = 8  # Fixed LED count
                mutated['duration'] = pattern.get('duration', 5000)
                
                # Ensure all required parameters exist before mutation
                if pattern['type'] == 'blink':
                    mutated['frequency'] = pattern.get('frequency', new_params['frequency'])
                    mutated['frequency'] = (
                        mutated['frequency'] * (1 - blend_factor) +
                        new_params['frequency'] * blend_factor
                    )
                    mutated['duty_cycle'] = new_params.get('duty_cycle', 0.4)
                    mutated['color'] = new_params['color']
                
                elif pattern['type'] == 'fade':
                    mutated['steps'] = pattern.get('steps', new_params['steps'])
                    mutated['steps'] = int(
                        mutated['steps'] * (1 - blend_factor) +
                        new_params['steps'] * blend_factor
                    )
                    mutated['fade_type'] = new_params['fade_type']
                    mutated['start_color'] = new_params['start_color']
                    mutated['end_color'] = new_params['end_color']
                
                elif pattern['type'] == 'wave':
                    mutated['speed'] = pattern.get('speed', new_params['speed'])
                    mutated['speed'] = (
                        mutated['speed'] * (1 - blend_factor) +
                        new_params['speed'] * blend_factor
                    )
                    mutated['wave_length'] = new_params['wave_length']
                    mutated['wave_type'] = new_params['wave_type']
                    mutated['color'] = new_params['color']
                
                elif pattern['type'] == 'pulse':
                    mutated['pulse_speed'] = pattern.get('pulse_speed', new_params['pulse_speed'])
                    mutated['pulse_speed'] = (
                        mutated['pulse_speed'] * (1 - blend_factor) +
                        new_params['pulse_speed'] * blend_factor
                    )
                    mutated['min_brightness'] = new_params['min_brightness']
                    mutated['max_brightness'] = new_params['max_brightness']
                    mutated['pulse_type'] = new_params['pulse_type']
                    mutated['color'] = new_params['color']
                
                elif pattern['type'] == 'solid':
                    mutated['brightness'] = new_params['brightness']
                    mutated['pulse_subtle'] = new_params['pulse_subtle']
                    mutated['color'] = new_params['color']
            
            return mutated
            
        except Exception as e:
            print(f"Error in mutation: {str(e)}")
            # If mutation fails, generate fresh parameters
            return self._generate_emotion_based_parameters(pattern['type'], target_emotion) 