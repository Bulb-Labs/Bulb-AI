# ai/agents/emotions/emotion_types.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set
import math
import time

class EmotionDimension(Enum):
    """Core dimensions for representing emotions"""
    VALENCE = "valence"  # Positive vs. negative (-1.0 to 1.0)
    AROUSAL = "arousal"  # Calm vs. excited (0.0 to 1.0)
    DOMINANCE = "dominance"  # Submissive vs. dominant (0.0 to 1.0)

class EmotionType(Enum):
    """Primary emotion types based on psychological models"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    
    # Complex emotions (combinations of primary emotions)
    LOVE = "love"  # Joy + Trust
    GUILT = "guilt"  # Sadness + Fear
    JEALOUSY = "jealousy"  # Anger + Fear
    HOPE = "hope"  # Anticipation + Joy
    DISAPPOINTMENT = "disappointment"  # Sadness + Surprise

@dataclass
class EmotionState:
    """Representation of an emotion with intensity and dimensions"""
    type: EmotionType
    intensity: float  # 0.0 to 1.0
    dimensions: Dict[EmotionDimension, float]
    cause: Optional[str] = None
    trigger_time: float = time.time()
    decay_rate: float = 0.1  # How quickly emotion fades per update
    
    def get_dimensional_value(self, dimension: EmotionDimension) -> float:
        """Get the value for a specific emotional dimension"""
        return self.dimensions.get(dimension, 0.0) * self.intensity
    
    def update(self, elapsed_time: float) -> None:
        """Update emotion intensity based on elapsed time"""
        decay = self.decay_rate * elapsed_time
        self.intensity = max(0.0, self.intensity - decay)

# ai/agents/emotions/emotion_engine.py
from typing import Dict, List, Optional, Set, Tuple, Any
import time
import math
import random
from .emotion_types import EmotionType, EmotionDimension, EmotionState

class EmotionEngine:
    """Engine for managing agent emotions"""
    
    # Dimensional profiles for each emotion type
    EMOTION_PROFILES = {
        EmotionType.JOY: {
            EmotionDimension.VALENCE: 1.0,
            EmotionDimension.AROUSAL: 0.7,
            EmotionDimension.DOMINANCE: 0.6
        },
        EmotionType.SADNESS: {
            EmotionDimension.VALENCE: -0.8,
            EmotionDimension.AROUSAL: 0.3,
            EmotionDimension.DOMINANCE: 0.2
        },
        EmotionType.ANGER: {
            EmotionDimension.VALENCE: -0.7,
            EmotionDimension.AROUSAL: 0.9,
            EmotionDimension.DOMINANCE: 0.8
        },
        EmotionType.FEAR: {
            EmotionDimension.VALENCE: -0.9,
            EmotionDimension.AROUSAL: 0.8,
            EmotionDimension.DOMINANCE: 0.1
        },
        EmotionType.DISGUST: {
            EmotionDimension.VALENCE: -0.8,
            EmotionDimension.AROUSAL: 0.6,
            EmotionDimension.DOMINANCE: 0.5
        },
        EmotionType.SURPRISE: {
            EmotionDimension.VALENCE: 0.1,  # Can be positive or negative
            EmotionDimension.AROUSAL: 0.9,
            EmotionDimension.DOMINANCE: 0.5
        },
        EmotionType.ANTICIPATION: {
            EmotionDimension.VALENCE: 0.3,
            EmotionDimension.AROUSAL: 0.7,
            EmotionDimension.DOMINANCE: 0.6
        },
        EmotionType.TRUST: {
            EmotionDimension.VALENCE: 0.7,
            EmotionDimension.AROUSAL: 0.3,
            EmotionDimension.DOMINANCE: 0.5
        },
        # Complex emotions
        EmotionType.LOVE: {
            EmotionDimension.VALENCE: 1.0,
            EmotionDimension.AROUSAL: 0.6,
            EmotionDimension.DOMINANCE: 0.7
        },
        EmotionType.GUILT: {
            EmotionDimension.VALENCE: -0.8,
            EmotionDimension.AROUSAL: 0.5,
            EmotionDimension.DOMINANCE: 0.1
        },
        EmotionType.JEALOUSY: {
            EmotionDimension.VALENCE: -0.7,
            EmotionDimension.AROUSAL: 0.8,
            EmotionDimension.DOMINANCE: 0.4
        },
        EmotionType.HOPE: {
            EmotionDimension.VALENCE: 0.8,
            EmotionDimension.AROUSAL: 0.6,
            EmotionDimension.DOMINANCE: 0.7
        },
        EmotionType.DISAPPOINTMENT: {
            EmotionDimension.VALENCE: -0.7,
            EmotionDimension.AROUSAL: 0.4,
            EmotionDimension.DOMINANCE: 0.3
        }
    }
    
    def __init__(self, agent_id: str, personality_traits: Dict[str, float] = None):
        self.agent_id = agent_id
        self.active_emotions: Dict[EmotionType, EmotionState] = {}
        self.emotion_history: List[EmotionState] = []
        self.last_update_time = time.time()
        self.personality_traits = personality_traits or {}
        self.mood = {
            EmotionDimension.VALENCE: 0.0,
            EmotionDimension.AROUSAL: 0.5,
            EmotionDimension.DOMINANCE: 0.5
        }
        self.mood_inertia = 0.8  # How resistant mood is to change (0-1)
        
    def generate_emotion(self, emotion_type: EmotionType, intensity: float, cause: str) -> EmotionState:
        """Generate a new emotion or intensify an existing one"""
        # Get the dimensional profile for this emotion
        profile = self.EMOTION_PROFILES[emotion_type].copy()
        
        # Create the emotion state
        emotion = EmotionState(
            type=emotion_type,
            intensity=min(1.0, intensity),
            dimensions=profile,
            cause=cause,
            trigger_time=time.time()
        )
        
        # Apply personality modifiers
        self._apply_personality_modifiers(emotion)
        
        # Store or update emotion
        if emotion_type in self.active_emotions:
            # Blend with existing emotion
            existing = self.active_emotions[emotion_type]
            existing.intensity = min(1.0, existing.intensity + intensity * 0.5)
            existing.cause = cause
            existing.trigger_time = time.time()
        else:
            self.active_emotions[emotion_type] = emotion
            
        # Update the agent's mood
        self._update_mood(emotion)
        
        # Add to history
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
            
        return emotion
    
    def update(self) -> None:
        """Update all active emotions (called periodically)"""
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update active emotions and remove expired ones
        expired = []
        for emotion_type, emotion in self.active_emotions.items():
            emotion.update(elapsed_time)
            if emotion.intensity <= 0.01:
                expired.append(emotion_type)
                
        for emotion_type in expired:
            del self.active_emotions[emotion_type]
            
        # Gradually return mood to baseline
        for dimension in EmotionDimension:
            baseline = 0.0 if dimension == EmotionDimension.VALENCE else 0.5
            self.mood[dimension] += (baseline - self.mood[dimension]) * (1 - self.mood_inertia) * elapsed_time
    
    def get_dominant_emotion(self) -> Optional[EmotionState]:
        """Get the most intense emotion currently active"""
        if not self.active_emotions:
            return None
            
        return max(self.active_emotions.values(), key=lambda e: e.intensity)
    
    def get_current_mood(self) -> Dict[EmotionDimension, float]:
        """Get the current mood state"""
        return self.mood.copy()
    
    def get_emotional_blend(self) -> Dict[EmotionDimension, float]:
        """Get the blended dimensional values of all active emotions"""
        result = {dim: 0.0 for dim in EmotionDimension}
        total_intensity = 0.0
        
        for emotion in self.active_emotions.values():
            for dimension, value in emotion.dimensions.items():
                result[dimension] += value * emotion.intensity
            total_intensity += emotion.intensity
            
        if total_intensity > 0:
            for dimension in result:
                result[dimension] /= total_intensity
                
        return result
    
    def emotional_response(self, 
                          stimulus: Dict[str, Any], 
                          context: Dict[str, Any] = None) -> List[EmotionState]:
        """Generate emotional responses to a stimulus"""
        emotions = []
        
        # Process the stimulus based on its type
        stimulus_type = stimulus.get("type", "neutral")
        intensity = stimulus.get("intensity", 0.5)
        source = stimulus.get("source", "unknown")
        valence = stimulus.get("valence", 0.0)
        
        # Apply personality and relationship modifiers
        source_relationship = context.get("relationships", {}).get(source, 0.0) if context else 0.0
        intensity *= 1.0 + (source_relationship * 0.5)
        
        # Generate emotions based on stimulus
        if stimulus_type == "threat":
            emotions.append(self.generate_emotion(EmotionType.FEAR, intensity, f"Threat from {source}"))
            if source_relationship < 0:
                emotions.append(self.generate_emotion(EmotionType.ANGER, intensity * 0.7, f"Threat from disliked source {source}"))
                
        elif stimulus_type == "cooperation":
            emotions.append(self.generate_emotion(EmotionType.TRUST, intensity, f"Cooperation with {source}"))
            if source_relationship > 0:
                emotions.append(self.generate_emotion(EmotionType.JOY, intensity * 0.5, f"Cooperation with liked source {source}"))
                
        elif stimulus_type == "conflict":
            emotions.append(self.generate_emotion(EmotionType.ANGER, intensity, f"Conflict with {source}"))
            
        elif stimulus_type == "surprise":
            surprise = self.generate_emotion(EmotionType.SURPRISE, intensity, f"Unexpected event from {source}")
            emotions.append(surprise)
            
            # Secondary emotion based on valence
            if valence > 0.3:
                emotions.append(self.generate_emotion(EmotionType.JOY, intensity * valence, f"Positive surprise from {source}"))
            elif valence < -0.3:
                emotions.append(self.generate_emotion(EmotionType.FEAR, intensity * -valence, f"Negative surprise from {source}"))
                
        # Add randomness for more diverse emotions (low probability)
        if random.random() < 0.1:
            random_emotion = random.choice(list(EmotionType))
            random_intensity = random.uniform(0.1, 0.3)
            emotions.append(self.generate_emotion(random_emotion, random_intensity, "Random emotional fluctuation"))
            
        return emotions
    
    def _apply_personality_modifiers(self, emotion: EmotionState) -> None:
        """Apply personality traits to emotion intensity and dimensions"""
        # Example personality effects:
        # - Neuroticism increases negative emotion intensity
        # - Extraversion increases arousal
        # - Agreeableness reduces anger intensity
        
        if "neuroticism" in self.personality_traits:
            neuroticism = self.personality_traits["neuroticism"]
            if emotion.dimensions[EmotionDimension.VALENCE] < 0:
                emotion.intensity *= 1.0 + (neuroticism * 0.5)
                
        if "extraversion" in self.personality_traits:
            extraversion = self.personality_traits["extraversion"]
            emotion.dimensions[EmotionDimension.AROUSAL] *= 1.0 + (extraversion * 0.3)
            
        if "agreeableness" in self.personality_traits and emotion.type == EmotionType.ANGER:
            agreeableness = self.personality_traits["agreeableness"]
            emotion.intensity *= 1.0 - (agreeableness * 0.4)
    
    def _update_mood(self, emotion: EmotionState) -> None:
        """Update mood based on a new emotion"""
        # Mood changes more slowly than emotions
        for dimension, value in emotion.dimensions.items():
            current = self.mood[dimension]
            # Calculate new mood as weighted average of current mood and emotion
            weight = emotion.intensity * (1.0 - self.mood_inertia)
            self.mood[dimension] = (current * (1.0 - weight)) + (value * weight)

# ai/agents/emotions/emotion_effects.py
from typing import Dict, Any, List, Callable
import math
from .emotion_types import EmotionDimension, EmotionType, EmotionState

class ActionModifier:
    """Represents a modification to an action based on emotional state"""
    def __init__(self, dimension: EmotionDimension, parameter: str, 
                 mapping_function: Callable[[float], float]):
        self.dimension = dimension
        self.parameter = parameter
        self.mapping_function = mapping_function

class EmotionEffects:
    """Manages the effects of emotions on agent behavior and decision-making"""
    
    def __init__(self, emotion_engine):
        self.emotion_engine = emotion_engine
        self.action_modifiers: Dict[str, List[ActionModifier]] = self._setup_modifiers()
        
    def _setup_modifiers(self) -> Dict[str, List[ActionModifier]]:
        """Set up the default action modifiers"""
        modifiers = {}
        
        # Modifiers for "communicate" action
        modifiers["communicate"] = [
            # Valence affects message tone
            ActionModifier(
                EmotionDimension.VALENCE,
                "tone",
                lambda x: x  # Linear mapping
            ),
            # Arousal affects message length and complexity
            ActionModifier(
                EmotionDimension.AROUSAL,
                "verbosity",
                lambda x: 1.0 + (x - 0.5) * 0.5  # Range from 0.75 to 1.25
            ),
            # Dominance affects forcefulness
            ActionModifier(
                EmotionDimension.DOMINANCE,
                "forcefulness",
                lambda x: x  # Linear mapping
            )
        ]
        
        # Modifiers for "analyze" action
        modifiers["analyze"] = [
            # Valence affects optimism in analysis
            ActionModifier(
                EmotionDimension.VALENCE,
                "optimism_bias",
                lambda x: x  # Linear mapping
            ),
            # Arousal affects depth vs. breadth
            ActionModifier(
                EmotionDimension.AROUSAL,
                "breadth_vs_depth",
                lambda x: 2.0 * abs(x - 0.5)  # High at extremes
            )
        ]
        
        # Modifiers for "decide" action
        modifiers["decide"] = [
            # Valence affects risk aversion
            ActionModifier(
                EmotionDimension.VALENCE,
                "risk_aversion",
                lambda x: 1.0 - x  # Negative mapping
            ),
            # Arousal affects decision speed
            ActionModifier(
                EmotionDimension.AROUSAL,
                "speed",
                lambda x: x  # Linear mapping
            ),
            # Dominance affects confidence
            ActionModifier(
                EmotionDimension.DOMINANCE,
                "confidence",
                lambda x: 0.5 + (x * 0.5)  # Range from 0.5 to 1.0
            )
        ]
        
        return modifiers
    
    def apply_emotion_effects(self, action_name: str, action_params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply emotional effects to action parameters"""
        if action_name not in self.action_modifiers:
            return action_params
            
        # Get current emotional state
        blend = self.emotion_engine.get_emotional_blend()
        dominant = self.emotion_engine.get_dominant_emotion()
        
        # Create a copy of the parameters to modify
        modified_params = action_params.copy()
        
        # Apply dimensional modifiers
        for modifier in self.action_modifiers[action_name]:
            if modifier.parameter not in modified_params:
                modified_params[modifier.parameter] = 0.5  # Default value
                
            dimension_value = blend[modifier.dimension]
            modified_value = modifier.mapping_function(dimension_value)
            modified_params[modifier.parameter] = modified_value
            
        # Apply special effects for specific emotion types
        if dominant:
            if dominant.type == EmotionType.ANGER and dominant.intensity > 0.7:
                if action_name == "communicate":
                    modified_params["tone"] = -0.8  # Very negative tone
                    modified_params["forcefulness"] = 0.9  # Very forceful
                    
            elif dominant.type == EmotionType.FEAR and dominant.intensity > 0.7:
                if action_name == "decide":
                    modified_params["risk_aversion"] = 0.9  # Very risk-averse
                    
        return modified_params
    
    def get_expression(self) -> Dict[str, Any]:
        """Get the emotional expression based on current state"""
        dominant = self.emotion_engine.get_dominant_emotion()
        blend = self.emotion_engine.get_emotional_blend()
        
        if not dominant:
            return {
                "expression": "neutral",
                "intensity": 0.0,
                "description": "Neutral expression"
            }
            
        # Map emotion types to expressions
        expression_map = {
            EmotionType.JOY: "happy",
            EmotionType.SADNESS: "sad",
            EmotionType.ANGER: "angry",
            EmotionType.FEAR: "fearful",
            EmotionType.DISGUST: "disgusted",
            EmotionType.SURPRISE: "surprised",
            EmotionType.ANTICIPATION: "interested",
            EmotionType.TRUST: "relaxed",
            EmotionType.LOVE: "loving",
            EmotionType.GUILT: "ashamed",
            EmotionType.JEALOUSY: "envious",
            EmotionType.HOPE: "hopeful",
            EmotionType.DISAPPOINTMENT: "disappointed"
        }
        
        # Generate description based on intensity
        intensity_descriptors = {
            (0.0, 0.3): "slightly",
            (0.3, 0.6): "moderately",
            (0.6, 0.8): "very",
            (0.8, 1.0): "extremely"
        }
        
        intensity_word = "somewhat"
        for range_tuple, descriptor in intensity_descriptors.items():
            if range_tuple[0] <= dominant.intensity < range_tuple[1]:
                intensity_word = descriptor
                break
                
        expression = expression_map.get(dominant.type, "neutral")
        description = f"{intensity_word} {expression}"
        
        return {
            "expression": expression,
            "intensity": dominant.intensity,
            "description": description,
            "dimensions": {dim.value: val for dim, val in blend.items()}
        }