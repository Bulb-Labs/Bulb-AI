from typing import Dict, Any, Optional, Type
from .base_agent import BaseAgent
from .personality import PersonalitySystem
from .behavior import BehaviorNode
import importlib
import json

class AgentFactory:
    def __init__(self):
        self._agent_types: Dict[str, Type[BaseAgent]] = {}
        self._default_personalities: Dict[str, Dict[str, float]] = {
            "friendly": {
                "openness": 0.7,
                "conscientiousness": 0.6,
                "extraversion": 0.8,
                "agreeableness": 0.9,
                "neuroticism": 0.3
            },
            "analytical": {
                "openness": 0.8,
                "conscientiousness": 0.9,
                "extraversion": 0.4,
                "agreeableness": 0.6,
                "neuroticism": 0.3
            },
            "creative": {
                "openness": 0.9,
                "conscientiousness": 0.5,
                "extraversion": 0.6,
                "agreeableness": 0.7,
                "neuroticism": 0.4
            }
        }

    def register_agent_type(self, type_name: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type"""
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"{agent_class.__name__} must inherit from BaseAgent")
        self._agent_types[type_name] = agent_class

    def register_personality_template(self, template_name: str, traits: Dict[str, float]) -> None:
        """Register a new personality template"""
        for trait, value in traits.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Trait values must be between 0 and 1. Invalid value for {trait}: {value}")
        self._default_personalities[template_name] = traits

    def create_agent(self, 
                    agent_type: str,
                    name: str,
                    personality_template: Optional[str] = None,
                    custom_personality: Optional[Dict[str, float]] = None,
                    config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """
        Create a new agent with specified configuration
        
        Args:
            agent_type: Type of agent to create
            name: Name of the agent
            personality_template: Name of predefined personality template
            custom_personality: Custom personality traits
            config: Additional configuration options
        """
        if agent_type not in self._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Determine personality traits
        personality_traits = {}
        if personality_template:
            if personality_template not in self._default_personalities:
                raise ValueError(f"Unknown personality template: {personality_template}")
            personality_traits = self._default_personalities[personality_template].copy()
        if custom_personality:
            personality_traits.update(custom_personality)

        # Create agent instance
        agent_class = self._agent_types[agent_type]
        agent = agent_class(name=name, personality_traits=personality_traits)
        
        # Apply additional configuration
        if config:
            for key, value in config.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)

        return agent

    def create_from_config(self, config_path: str) -> Dict[str, BaseAgent]:
        """Create multiple agents from a configuration file"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        agents = {}
        for agent_config in config['agents']:
            agent = self.create_agent(**agent_config)
            agents[agent.id] = agent
        
        return agents

    @classmethod
    def load_agent_types(cls, module_path: str) -> Dict[str, Type[BaseAgent]]:
        """Dynamically load agent types from a module"""
        try:
            module = importlib.import_module(module_path)
            agent_types = {}
            
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, BaseAgent) and 
                    item != BaseAgent):
                    agent_types[item_name.lower()] = item
                    
            return agent_types
        except ImportError as e:
            raise ImportError(f"Failed to load agent types from {module_path}: {e}")