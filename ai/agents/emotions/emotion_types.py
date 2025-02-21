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