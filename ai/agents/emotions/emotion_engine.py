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
