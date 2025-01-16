from typing import Dict, Any, List
import math

class PersonalitySystem:
    def __init__(self, base_traits: Dict[str, float] = None):
        self.traits = base_traits or {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
        self.mood = {
            "happiness": 0.5,
            "energy": 0.5,
            "stress": 0.5
        }
    
    def adjust_trait(self, trait: str, amount: float) -> None:
        """Adjust a personality trait within bounds"""
        if trait in self.traits:
            self.traits[trait] = max(0.0, min(1.0, self.traits[trait] + amount))
    
    def update_mood(self, events: List[Dict[str, Any]]) -> None:
        """Update mood based on recent events"""
        for event in events:
            impact = event.get("emotional_impact", {})
            for mood_type, change in impact.items():
                if mood_type in self.mood:
                    self.mood[mood_type] = max(0.0, min(1.0, self.mood[mood_type] + change))
    
    def get_response_modifiers(self) -> Dict[str, float]:
        """Calculate response modifiers based on personality and mood"""
        return {
            "enthusiasm": (self.traits["extraversion"] * self.mood["energy"]),
            "positivity": (self.traits["agreeableness"] * self.mood["happiness"]),
            "detail": (self.traits["conscientiousness"] * (1 - self.mood["stress"]))
        }