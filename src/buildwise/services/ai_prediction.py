"""AI-powered prediction services for BuildWise CLI."""

import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from buildwise.config.settings import settings

# Import OpenAI API conditionally (for offline fallback)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class PredictionType(str, Enum):
    """Types of predictions supported."""
    
    MATERIAL_COST = "material_cost"
    LABOR_COST = "labor_cost"
    PROJECT_TIMELINE = "project_timeline"
    MATERIAL_QUANTITY = "material_quantity"


class AIPredictionService:
    """Service for AI-powered predictions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI prediction service.
        
        Args:
            api_key: OpenAI API key (optional, will use settings or env var if not provided)
        """
        self.api_key = api_key or settings.openai_api_key
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if the AI prediction service is available.
        
        Returns:
            True if the service is available, False otherwise
        """
        return self.client is not None
    
    def set_api_key(self, api_key: str) -> bool:
        """Set the OpenAI API key.
        
        Args:
            api_key: OpenAI API key
            
        Returns:
            True if successful, False otherwise
        """
        self.api_key = api_key
        settings.openai_api_key = api_key
        
        if OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=self.api_key)
                return True
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                return False
        
        return False
    
    def predict_material_cost(
        self,
        material_type: str,
        quantity: Union[float, Dict[str, float]],
        location: str,
        date: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Predict material cost based on type, quantity, and location.
        
        Args:
            material_type: Type of material (concrete, lumber, etc.)
            quantity: Amount of material or calculation result
            location: Geographic location for pricing
            date: Optional date for historical or future pricing
            details: Additional details for the prediction
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_available():
            return self._fallback_prediction(
                prediction_type=PredictionType.MATERIAL_COST,
                material_type=material_type,
                quantity=quantity,
                location=location
            )
        
        # Extract quantity value if it's a calculation result
        quantity_value = quantity
        if isinstance(quantity, dict):
            if "board_feet" in quantity:
                quantity_value = quantity["board_feet"]
            elif "cubic_yards" in quantity:
                quantity_value = quantity["cubic_yards"]
        
        # Prepare the prompt for the AI
        prompt = f"""
        I need a cost estimate for the following construction material:
        
        Material: {material_type}
        Quantity: {quantity_value} {"board feet" if "board_feet" in str(quantity) else "cubic yards" if "cubic_yards" in str(quantity) else "units"}
        Location: {location}
        {"Date: " + date if date else ""}
        
        {json.dumps(details) if details else ""}
        
        Please provide:
        1. The estimated cost in USD
        2. A cost range (min-max)
        3. Factors affecting this price
        4. Confidence level of this prediction (low, medium, high)
        
        Format your response as a JSON object with fields: estimated_cost, min_cost, max_cost, factors, confidence_level
        """
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert construction cost estimator. Provide factual, current estimates based on market data. Format responses as JSON objects."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                
                # Add metadata
                result["source"] = "openai"
                result["prediction_type"] = PredictionType.MATERIAL_COST.value
                
                return result
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                return self._fallback_prediction(
                    prediction_type=PredictionType.MATERIAL_COST,
                    material_type=material_type,
                    quantity=quantity,
                    location=location
                )
                
        except Exception as e:
            print(f"Error during AI prediction: {e}")
            return self._fallback_prediction(
                prediction_type=PredictionType.MATERIAL_COST,
                material_type=material_type,
                quantity=quantity,
                location=location
            )
    
    def predict_labor_cost(
        self,
        project_type: str,
        scope: Dict[str, Any],
        location: str,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Predict labor cost based on project type, scope, and location.
        
        Args:
            project_type: Type of project (residential, commercial, etc.)
            scope: Project scope details
            location: Geographic location for pricing
            date: Optional date for historical or future pricing
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_available():
            return self._fallback_prediction(
                prediction_type=PredictionType.LABOR_COST,
                project_type=project_type,
                scope=scope,
                location=location
            )
        
        # Prepare the prompt for the AI
        prompt = f"""
        I need a labor cost estimate for the following construction project:
        
        Project Type: {project_type}
        Scope: {json.dumps(scope)}
        Location: {location}
        {"Date: " + date if date else ""}
        
        Please provide:
        1. The estimated labor cost in USD
        2. A cost range (min-max)
        3. Estimated hours required
        4. Hourly rate assumptions
        5. Factors affecting this price
        6. Confidence level of this prediction (low, medium, high)
        
        Format your response as a JSON object with fields: estimated_cost, min_cost, max_cost, estimated_hours, hourly_rate, factors, confidence_level
        """
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert construction estimator. Provide factual, current labor estimates based on market data. Format responses as JSON objects."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                
                # Add metadata
                result["source"] = "openai"
                result["prediction_type"] = PredictionType.LABOR_COST.value
                
                return result
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                return self._fallback_prediction(
                    prediction_type=PredictionType.LABOR_COST,
                    project_type=project_type,
                    scope=scope,
                    location=location
                )
                
        except Exception as e:
            print(f"Error during AI prediction: {e}")
            return self._fallback_prediction(
                prediction_type=PredictionType.LABOR_COST,
                project_type=project_type,
                scope=scope,
                location=location
            )
    
    def predict_project_timeline(
        self,
        project_type: str,
        scope: Dict[str, Any],
        location: str
    ) -> Dict[str, Any]:
        """Predict project timeline based on type, scope, and location.
        
        Args:
            project_type: Type of project (residential, commercial, etc.)
            scope: Project scope details
            location: Geographic location
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_available():
            return self._fallback_prediction(
                prediction_type=PredictionType.PROJECT_TIMELINE,
                project_type=project_type,
                scope=scope,
                location=location
            )
        
        # Prepare the prompt for the AI
        prompt = f"""
        I need a timeline estimate for the following construction project:
        
        Project Type: {project_type}
        Scope: {json.dumps(scope)}
        Location: {location}
        
        Please provide:
        1. The estimated duration in days
        2. A duration range (min-max days)
        3. Key milestones with estimated durations
        4. Factors affecting this timeline
        5. Confidence level of this prediction (low, medium, high)
        
        Format your response as a JSON object with fields: estimated_duration, min_duration, max_duration, milestones, factors, confidence_level
        """
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert construction project manager. Provide factual timeline estimates based on industry standards. Format responses as JSON objects."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                
                # Add metadata
                result["source"] = "openai"
                result["prediction_type"] = PredictionType.PROJECT_TIMELINE.value
                
                return result
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                return self._fallback_prediction(
                    prediction_type=PredictionType.PROJECT_TIMELINE,
                    project_type=project_type,
                    scope=scope,
                    location=location
                )
                
        except Exception as e:
            print(f"Error during AI prediction: {e}")
            return self._fallback_prediction(
                prediction_type=PredictionType.PROJECT_TIMELINE,
                project_type=project_type,
                scope=scope,
                location=location
            )
    
    def _fallback_prediction(
        self,
        prediction_type: PredictionType,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate fallback predictions when AI is unavailable.
        
        Args:
            prediction_type: Type of prediction to generate
            **kwargs: Additional parameters for the prediction
            
        Returns:
            Dictionary with fallback prediction results
        """
        if prediction_type == PredictionType.MATERIAL_COST:
            material_type = kwargs.get("material_type", "")
            quantity = kwargs.get("quantity", 0)
            location = kwargs.get("location", "")
            
            # Extract quantity value if it's a calculation result
            quantity_value = quantity
            if isinstance(quantity, dict):
                if "board_feet" in quantity:
                    quantity_value = quantity["board_feet"]
                elif "cubic_yards" in quantity:
                    quantity_value = quantity["cubic_yards"]
            
            # Base prices for common materials from settings
            material_prices = settings.material_prices
            
            base_prices = {
                "concrete": material_prices.get("concrete_per_yard", 150),  # per cubic yard
                "lumber": material_prices.get("lumber_pine_per_bf", 3.0),   # per board foot (pine)
                "steel": material_prices.get("steel_per_pound", 0.85),      # per pound
                "plywood": material_prices.get("plywood_per_sheet", 50),    # per 4x8 sheet
                "drywall": material_prices.get("drywall_per_sheet", 15),    # per 4x8 sheet
                "roofing": material_prices.get("roofing_per_square", 100),  # per square (100 sq ft)
                "siding": material_prices.get("siding_per_sqft", 10),       # per sq ft
                "insulation": material_prices.get("insulation_per_sqft", 0.7), # per sq ft
            }
            
            # Location factors (very approximate)
            location_factors = {
                "new york": 1.3,
                "california": 1.25,
                "texas": 0.95,
                "florida": 1.05,
                "illinois": 1.1,
                "ohio": 0.9,
                "michigan": 0.95,
                "pennsylvania": 1.0,
                "georgia": 0.9,
                "north carolina": 0.9,
                "new jersey": 1.15,
                "virginia": 1.0,
                "washington": 1.1,
                "massachusetts": 1.2,
                "indiana": 0.85,
                "arizona": 1.0,
                "tennessee": 0.85,
                "missouri": 0.9,
                "maryland": 1.05,
                "wisconsin": 0.9,
                "minnesota": 0.95,
                "colorado": 1.05,
                "alabama": 0.8,
                "south carolina": 0.85,
                "louisiana": 0.9,
                "kentucky": 0.85,
                "oregon": 1.05,
                "oklahoma": 0.85,
                "connecticut": 1.15,
                "utah": 0.95,
                "iowa": 0.85,
                "nevada": 1.05,
                "arkansas": 0.8,
                "mississippi": 0.8,
                "kansas": 0.85,
                "new mexico": 0.9,
                "nebraska": 0.85,
                "west virginia": 0.8,
                "idaho": 0.9,
                "hawaii": 1.5,
                "maine": 1.0,
                "new hampshire": 1.05,
                "rhode island": 1.1,
                "montana": 0.9,
                "delaware": 1.0,
                "south dakota": 0.85,
                "north dakota": 0.9,
                "alaska": 1.45,
                "vermont": 1.0,
                "wyoming": 0.9,
            }
            
            # Find closest material
            material_price = None
            for key, price in base_prices.items():
                if material_type.lower() in key or key in material_type.lower():
                    material_price = price
                    break
            
            if material_price is None:
                material_price = 100  # Default fallback price
            
            # Find location factor
            location_factor = 1.0  # Default
            location_lower = location.lower()
            for loc, factor in location_factors.items():
                if loc in location_lower:
                    location_factor = factor
                    break
            
            # Calculate estimated cost
            try:
                estimated_cost = float(quantity_value) * material_price * location_factor
            except (ValueError, TypeError):
                estimated_cost = 0.0
            
            # Calculate range (±15%)
            min_cost = estimated_cost * 0.85
            max_cost = estimated_cost * 1.15
            
            return {
                "estimated_cost": round(estimated_cost, 2),
                "min_cost": round(min_cost, 2),
                "max_cost": round(max_cost, 2),
                "factors": [
                    "Base material price",
                    "Regional cost variations",
                    "Seasonal price fluctuations",
                    "Quality and grade differences"
                ],
                "confidence_level": "low",
                "source": "fallback",
                "prediction_type": prediction_type.value
            }
            
        elif prediction_type == PredictionType.LABOR_COST:
            project_type = kwargs.get("project_type", "")
            scope = kwargs.get("scope", {})
            location = kwargs.get("location", "")
            
            # Very basic implementation for fallback
            # Actual implementation would be much more sophisticated
            
            base_rate = 50  # Base hourly rate
            hours = 40      # Default hours
            
            # Adjust based on project type
            if "commercial" in project_type.lower():
                base_rate *= 1.2
            elif "industrial" in project_type.lower():
                base_rate *= 1.5
            
            # Adjust based on location
            location_lower = location.lower()
            for loc, factor in {
                "new york": 1.3,
                "california": 1.25,
                "texas": 0.95,
                # Other regions as needed
            }.items():
                if loc in location_lower:
                    base_rate *= factor
                    break
            
            estimated_cost = base_rate * hours
            
            return {
                "estimated_cost": round(estimated_cost, 2),
                "min_cost": round(estimated_cost * 0.8, 2),
                "max_cost": round(estimated_cost * 1.3, 2),
                "hourly_rate": round(base_rate, 2),
                "estimated_hours": hours,
                "factors": [
                    "Labor market conditions",
                    "Project complexity",
                    "Regional wage differences",
                    "Contractor availability"
                ],
                "confidence_level": "low",
                "source": "fallback",
                "prediction_type": prediction_type.value
            }
        
        elif prediction_type == PredictionType.PROJECT_TIMELINE:
            project_type = kwargs.get("project_type", "")
            scope = kwargs.get("scope", {})
            
            # Very basic implementation for fallback
            if "residential" in project_type.lower():
                days = 90  # 3 months for residential
            elif "commercial" in project_type.lower():
                days = 180  # 6 months for commercial
            else:
                days = 120  # 4 months default
            
            return {
                "estimated_duration": days,
                "min_duration": int(days * 0.8),
                "max_duration": int(days * 1.3),
                "milestones": [
                    {"name": "Planning & Permits", "duration": int(days * 0.2)},
                    {"name": "Foundation", "duration": int(days * 0.15)},
                    {"name": "Framing", "duration": int(days * 0.2)},
                    {"name": "Mechanical & Electrical", "duration": int(days * 0.2)},
                    {"name": "Finishing", "duration": int(days * 0.25)}
                ],
                "factors": [
                    "Weather conditions",
                    "Permit processing times",
                    "Labor availability",
                    "Supply chain delays"
                ],
                "confidence_level": "low",
                "source": "fallback",
                "prediction_type": prediction_type.value
            }
        
        else:
            # Generic fallback for other prediction types
            return {
                "error": "Prediction type not supported in fallback mode",
                "source": "fallback",
                "prediction_type": prediction_type.value,
                "confidence_level": "none"
            }
