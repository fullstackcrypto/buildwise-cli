"""AI prediction service for BuildWise CLI."""
import os
from enum import Enum
from typing import Dict, Any, Optional

from buildwise.config.settings import settings

class PredictionType(str, Enum):
    """Types of predictions."""
    MATERIAL_COST = "material_cost"
    LABOR_COST = "labor_cost"
    PROJECT_TIMELINE = "project_timeline"
    MATERIAL_QUANTITY = "material_quantity"

class AIPredictionService:
    """Service for AI-powered predictions."""
    
    def __init__(self, model_path: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the service.
        
        Args:
            model_path: Path to local model file
            api_key: API key for external services
        """
        self.model_path = model_path
        self.api_key = api_key or settings.openai_api_key
        self.model = None
        self.client = None
        self.fallback_enabled = True
        
        # Initialize model or API client
        if self.model_path and os.path.exists(self.model_path):
            self.model = self._load_local_model()
        elif self.api_key:
            self.client = self._initialize_api_client()
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.model is not None or self.client is not None
    
    def set_api_key(self, api_key: str) -> bool:
        """Set API key."""
        try:
            self.api_key = api_key
            self.client = self._initialize_api_client()
            return True
        except Exception:
            return False
    
    def predict_material_cost(
        self, 
        material_type: str, 
        quantity: Dict[str, float], 
        location: str = "United States"
    ) -> Dict[str, Any]:
        """Predict material cost.
        
        Args:
            material_type: Type of material (concrete, lumber, steel)
            quantity: Quantity of material with units
            location: Location for pricing
        
        Returns:
            dict: Prediction results
        """
        try:
            # Prepare features
            features = self._prepare_features(
                material_type=material_type,
                quantity=quantity,
                location=location
            )
            
            # Get prediction
            if self.model:
                prediction = self._predict_with_local_model(features)
            elif self.client:
                prediction = self._predict_with_api(features)
            else:
                raise ValueError("No model or API client available")
            
            return {
                "estimated_cost": prediction["cost"],
                "min_cost": prediction.get("min_cost", prediction["cost"] * 0.9),
                "max_cost": prediction.get("max_cost", prediction["cost"] * 1.1),
                "confidence": prediction.get("confidence", 0.8),
                "source": "ai_model",
                "prediction_type": PredictionType.MATERIAL_COST
            }
        except Exception as e:
            if self.fallback_enabled:
                return self._fallback_prediction(material_type, quantity, location)
            raise e
    
    def predict_labor_cost(
        self, 
        project_type: str, 
        scope: Dict[str, Any], 
        location: str = "United States"
    ) -> Dict[str, Any]:
        """Predict labor cost."""
        # Implementation would be similar to predict_material_cost
        # For now, just use the fallback
        return self._fallback_prediction_labor(project_type, scope, location)
    
    def predict_project_timeline(
        self, 
        project_type: str, 
        scope: Dict[str, Any], 
        location: str = "United States"
    ) -> Dict[str, Any]:
        """Predict project timeline."""
        # Implementation would be similar to predict_material_cost
        # For now, just use the fallback
        return self._fallback_prediction_timeline(project_type, scope, location)
    
    def _load_local_model(self):
        """Load local model from file."""
        # In a real implementation, this would load a model from disk
        # For now, just return a dummy model
        return {"type": "dummy_model"}
    
    def _initialize_api_client(self):
        """Initialize API client."""
        # In a real implementation, this would initialize an API client
        # For now, just check if we have an API key
        if not self.api_key:
            return None
        
        try:
            # Try to import OpenAI
            import openai
            openai.api_key = self.api_key
            return openai
        except ImportError:
            # OpenAI package not installed
            return None
    
    def _prepare_features(self, **kwargs) -> Dict[str, Any]:
        """Prepare features for prediction."""
        # This would transform raw inputs into model features
        return kwargs
    
    def _predict_with_local_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction with local model."""
        # This would use the local model to make a prediction
        # For now, just return a dummy prediction
        material_type = features.get("material_type", "")
        quantity = features.get("quantity", {})
        location = features.get("location", "")
        
        # Get unit and value
        unit = next(iter(quantity.keys()), "")
        value = next(iter(quantity.values()), 0)
        
        # Base cost estimation
        if material_type == "concrete" and unit == "cubic_yards":
            cost = value * settings.material_prices.get("concrete_per_yard", 150)
        elif material_type == "lumber":
            cost = value * settings.material_prices.get("lumber_pine_per_bf", 3.0)
        elif material_type == "steel":
            cost = value * settings.material_prices.get("steel_per_pound", 0.85)
        else:
            cost = value * 100  # Default fallback
        
        # Apply location factor
        location_factors = {
            "New York": 1.2,
            "California": 1.15,
            "Texas": 0.9,
            "Florida": 0.95,
            "Illinois": 1.05,
            "United States": 1.0,
        }
        
        location_factor = location_factors.get(location, 1.0)
        cost *= location_factor
        
        return {
            "cost": cost,
            "confidence": 0.8,
            "min_cost": cost * 0.9,
            "max_cost": cost * 1.1
        }
    
    def _predict_with_api(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction with API."""
        # This would use an API to make a prediction
        # For now, just return a dummy prediction
        return self._predict_with_local_model(features)
    
    def _fallback_prediction(
        self,
        material_type: str, 
        quantity: Dict[str, float], 
        location: str = "United States"
    ) -> Dict[str, Any]:
        """Provide a fallback prediction using deterministic methods."""
        # Similar logic to _predict_with_local_model
        unit = next(iter(quantity.keys()), "")
        value = next(iter(quantity.values()), 0)
        
        # Base cost
        if material_type == "concrete" and unit == "cubic_yards":
            base_cost = settings.material_prices.get("concrete_per_yard", 150)
        elif material_type == "lumber":
            base_cost = settings.material_prices.get("lumber_pine_per_bf", 3.0)
        elif material_type == "steel":
            base_cost = settings.material_prices.get("steel_per_pound", 0.85)
        else:
            base_cost = 100  # Default fallback
        
        # Location factors
        location_factors = {
            "New York": 1.2,
            "California": 1.15,
            "Texas": 0.9,
            "Florida": 0.95,
            "Illinois": 1.05,
            "United States": 1.0,
        }
        
        location_factor = location_factors.get(location, 1.0)
        cost = value * base_cost * location_factor
        
        return {
            "estimated_cost": cost,
            "min_cost": cost * 0.85,
            "max_cost": cost * 1.15,
            "confidence": 0.7,  # Lower confidence for fallback
            "source": "fallback_calculation",
            "prediction_type": PredictionType.MATERIAL_COST
        }
    
    def _fallback_prediction_labor(
        self,
        project_type: str, 
        scope: Dict[str, Any], 
        location: str = "United States"
    ) -> Dict[str, Any]:
        """Provide a fallback labor cost prediction."""
        # Simplified estimation
        area = scope.get("area", 0)
        stories = scope.get("stories", 1)
        
        # Base labor rates by project type ($/sqft)
        labor_rates = {
            "residential": 30,
            "commercial": 45,
            "industrial": 55,
            "renovation": 40
        }
        
        base_rate = labor_rates.get(project_type.lower(), 35)
        
        # Location factors
        location_factors = {
            "New York": 1.3,
            "California": 1.25,
            "Texas": 0.9,
            "Florida": 0.95,
            "Illinois": 1.1,
            "United States": 1.0,
        }
        
        location_factor = location_factors.get(location, 1.0)
        
        # Calculate cost
        cost = area * base_rate * location_factor * (1 + (stories - 1) * 0.1)
        
        return {
            "estimated_cost": cost,
            "min_cost": cost * 0.8,
            "max_cost": cost * 1.2,
            "confidence": 0.65,
            "source": "fallback_calculation",
            "prediction_type": PredictionType.LABOR_COST
        }
    
    def _fallback_prediction_timeline(
        self,
        project_type: str, 
        scope: Dict[str, Any], 
        location: str = "United States"
    ) -> Dict[str, Any]:
        """Provide a fallback project timeline prediction."""
        # Simplified estimation
        area = scope.get("area", 0)
        stories = scope.get("stories", 1)
        
        # Base timeline by project type (days per 1000 sqft)
        timeline_rates = {
            "residential": 15,
            "commercial": 20,
            "industrial": 25,
            "renovation": 18
        }
        
        base_rate = timeline_rates.get(project_type.lower(), 18)
        
        # Calculate timeline in days
        days = (area / 1000) * base_rate * (1 + (stories - 1) * 0.2)
        
        return {
            "estimated_days": int(days),
            "min_days": int(days * 0.8),
            "max_days": int(days * 1.3),
            "confidence": 0.6,
            "source": "fallback_calculation",
            "prediction_type": PredictionType.PROJECT_TIMELINE
        }
