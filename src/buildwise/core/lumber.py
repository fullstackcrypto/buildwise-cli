"""Lumber calculator module for BuildWise CLI."""

from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from pint import UnitRegistry

# Initialize unit registry
ureg = UnitRegistry()


class LumberType(str, Enum):
    """Common lumber types."""
    
    PINE = "pine"
    FIR = "fir"
    CEDAR = "cedar"
    OAK = "oak"
    MAPLE = "maple"
    WALNUT = "walnut"
    REDWOOD = "redwood"
    SPRUCE = "spruce"
    CYPRESS = "cypress"
    POPLAR = "poplar"


class LumberGrade(str, Enum):
    """Common lumber grades."""
    
    SELECT = "select"
    ONE = "no.1"
    TWO = "no.2"
    THREE = "no.3"
    CONSTRUCTION = "construction"
    STANDARD = "standard"
    UTILITY = "utility"
    ECONOMY = "economy"
    STUD = "stud"
    CUSTOM = "custom"


class LumberCalculator:
    """Calculator for lumber quantities and cost estimation."""
    
    def __init__(self):
        """Initialize the lumber calculator."""
        self.ureg = UnitRegistry()
        self.Q_ = self.ureg.Quantity
        
        # Default prices per board foot (in USD) - approximate market values
        self._default_prices = {
            LumberType.PINE: {
                LumberGrade.SELECT: 4.50,
                LumberGrade.ONE: 3.75,
                LumberGrade.TWO: 3.00,
                LumberGrade.THREE: 2.25,
                LumberGrade.CONSTRUCTION: 2.50,
                LumberGrade.STANDARD: 2.00,
                LumberGrade.UTILITY: 1.75,
                LumberGrade.ECONOMY: 1.50,
                LumberGrade.STUD: 2.25,
                LumberGrade.CUSTOM: 5.00,
            },
            LumberType.FIR: {
                LumberGrade.SELECT: 5.25,
                LumberGrade.ONE: 4.50,
                LumberGrade.TWO: 3.75,
                LumberGrade.THREE: 3.00,
                LumberGrade.CONSTRUCTION: 3.50,
                LumberGrade.STANDARD: 3.25,
                LumberGrade.UTILITY: 2.75,
                LumberGrade.ECONOMY: 2.25,
                LumberGrade.STUD: 3.50,
                LumberGrade.CUSTOM: 6.00,
            },
            # Add more lumber types as needed
        }
        
        # Set default prices for other lumber types
        for lumber_type in LumberType:
            if lumber_type not in self._default_prices:
                if lumber_type in [LumberType.OAK, LumberType.MAPLE, LumberType.WALNUT]:
                    # Hardwoods are more expensive
                    self._default_prices[lumber_type] = {
                        grade: price * 2.5 for grade, price in self._default_prices[LumberType.PINE].items()
                    }
                elif lumber_type in [LumberType.CEDAR, LumberType.REDWOOD, LumberType.CYPRESS]:
                    # Outdoor/specialty woods
                    self._default_prices[lumber_type] = {
                        grade: price * 1.75 for grade, price in self._default_prices[LumberType.PINE].items()
                    }
                else:
                    # Other softwoods
                    self._default_prices[lumber_type] = {
                        grade: price * 1.1 for grade, price in self._default_prices[LumberType.PINE].items()
                    }
    
    def calculate_board_feet(
        self,
        nominal_width: Union[int, float, Decimal],
        nominal_thickness: Union[int, float, Decimal],
        length: Union[int, float, Decimal],
        quantity: int = 1,
        length_unit: str = "feet"
    ) -> Dict[str, Union[float, object]]:
        """Calculate board feet for lumber.
        
        Args:
            nominal_width: Nominal width in inches (e.g., 4 for a 2x4)
            nominal_thickness: Nominal thickness in inches (e.g., 2 for a 2x4)
            length: Length of the lumber
            quantity: Number of pieces
            length_unit: Unit for length (feet, meters, etc.)
            
        Returns:
            Dict containing board feet and actual dimensions
        """
        # Convert nominal dimensions to actual dimensions (standard conversion)
        # For 2x lumber, actual thickness is 1.5 inches
        # For 4x lumber, actual thickness is 3.5 inches
        # For width, subtract 0.5 inches for ≤6 inches, 0.75 inches for >6 inches
        if nominal_thickness < 2.5:  # 2x lumber
            actual_thickness = 1.5
        elif nominal_thickness < 4.5:  # 4x lumber
            actual_thickness = 3.5
        else:  # 6x or larger
            actual_thickness = nominal_thickness - 0.5
            
        if nominal_width <= 6:
            actual_width = nominal_width - 0.5
        else:
            actual_width = nominal_width - 0.75
        
        # Convert length to feet for board feet calculation
        length_q = self.Q_(float(length), length_unit)
        length_feet = length_q.to(self.ureg.foot).magnitude
        
        # Calculate board feet (width × thickness × length) ÷ 12
        # Where all dimensions are in inches, except length which is in feet
        board_feet = (actual_width * actual_thickness * length_feet) / 12 * quantity
        
        # Calculate total actual dimensions
        thickness_q = self.Q_(actual_thickness, 'inch')
        width_q = self.Q_(actual_width, 'inch')
        volume = thickness_q * width_q * length_q * quantity
        
        return {
            "board_feet": round(board_feet, 2),
            "actual_thickness": actual_thickness,
            "actual_width": actual_width,
            "length_feet": length_feet,
            "quantity": quantity,
            "volume": volume,
        }
    
    def calculate_cost(
        self,
        board_feet: Union[float, Dict[str, Union[float, object]]],
        lumber_type: Union[str, LumberType] = LumberType.PINE,
        grade: Union[str, LumberGrade] = LumberGrade.TWO,
        price_per_board_foot: Optional[float] = None
    ) -> float:
        """Calculate cost for lumber.
        
        Args:
            board_feet: Board feet value or result from calculate_board_feet
            lumber_type: Type of lumber (pine, oak, etc.)
            grade: Grade of lumber (select, no.1, etc.)
            price_per_board_foot: Custom price per board foot (overrides defaults)
            
        Returns:
            Total cost in USD
        """
        # Extract board feet if a dictionary is provided
        if isinstance(board_feet, dict) and "board_feet" in board_feet:
            board_feet_value = board_feet["board_feet"]
        else:
            board_feet_value = float(board_feet)
        
        # Convert string values to enum if needed
        if isinstance(lumber_type, str):
            lumber_type = LumberType(lumber_type.lower())
        
        if isinstance(grade, str):
            grade = LumberGrade(grade.lower())
        
        # Determine price per board foot
        if price_per_board_foot is not None:
            price = float(price_per_board_foot)
        else:
            price = self._default_prices.get(lumber_type, {}).get(grade, 3.0)
        
        # Calculate total cost
        cost = board_feet_value * price
        
        return round(cost, 2)
    
    def calculate_project(
        self,
        dimensions: List[Tuple[float, float, float, int]],
        lumber_type: Union[str, LumberType] = LumberType.PINE,
        grade: Union[str, LumberGrade] = LumberGrade.TWO,
        length_unit: str = "feet",
        price_per_board_foot: Optional[float] = None,
        waste_factor: float = 0.1  # 10% waste by default
    ) -> Dict[str, Union[float, List[Dict[str, Union[float, object]]]]]:
        """Calculate board feet and cost for a project with multiple lumber pieces.
        
        Args:
            dimensions: List of tuples (width, thickness, length, quantity)
            lumber_type: Type of lumber for the project
            grade: Grade of lumber for the project
            length_unit: Unit for length measurements
            price_per_board_foot: Custom price per board foot
            waste_factor: Percentage of waste to account for (0.1 = 10%)
            
        Returns:
            Dict with total board feet, cost, and individual calculations
        """
        calculations = []
        total_board_feet = 0
        
        for width, thickness, length, quantity in dimensions:
            result = self.calculate_board_feet(
                nominal_width=width,
                nominal_thickness=thickness,
                length=length,
                quantity=quantity,
                length_unit=length_unit
            )
            calculations.append(result)
            total_board_feet += result["board_feet"]
        
        # Apply waste factor
        total_board_feet_with_waste = total_board_feet * (1 + waste_factor)
        
        # Calculate cost
        cost = self.calculate_cost(
            board_feet=total_board_feet_with_waste,
            lumber_type=lumber_type,
            grade=grade,
            price_per_board_foot=price_per_board_foot
        )
        
        return {
            "board_feet": round(total_board_feet, 2),
            "board_feet_with_waste": round(total_board_feet_with_waste, 2),
            "waste_factor": waste_factor,
            "waste_board_feet": round(total_board_feet_with_waste - total_board_feet, 2),
            "cost": cost,
            "lumber_type": lumber_type if isinstance(lumber_type, str) else lumber_type.value,
            "grade": grade if isinstance(grade, str) else grade.value,
            "calculations": calculations,
        }
    
    def get_standard_sizes(self) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        """Get a list of standard lumber sizes.
        
        Returns:
            Dict of standard lumber dimensions by category
        """
        return {
            "dimensional_lumber": [
                {"thickness": 2, "width": 2, "description": "2×2"},
                {"thickness": 2, "width": 3, "description": "2×3"},
                {"thickness": 2, "width": 4, "description": "2×4"},
                {"thickness": 2, "width": 6, "description": "2×6"},
                {"thickness": 2, "width": 8, "description": "2×8"},
                {"thickness": 2, "width": 10, "description": "2×10"},
                {"thickness": 2, "width": 12, "description": "2×12"},
                {"thickness": 4, "width": 4, "description": "4×4"},
                {"thickness": 4, "width": 6, "description": "4×6"},
                {"thickness": 6, "width": 6, "description": "6×6"},
            ],
            "standard_lengths": [
                8, 10, 12, 14, 16, 18, 20, 22, 24
            ],
            "plywood": [
                {"thickness": 0.25, "width": 48, "length": 96, "description": "1/4\" × 4' × 8'"},
                {"thickness": 0.5, "width": 48, "length": 96, "description": "1/2\" × 4' × 8'"},
                {"thickness": 0.75, "width": 48, "length": 96, "description": "3/4\" × 4' × 8'"},
            ],
        }

class LumberCalculator:
    """Calculator for lumber quantities and cost estimation."""
    
    def __init__(self):
        """Initialize the lumber calculator."""
        self.ureg = UnitRegistry()
        self.Q_ = self.ureg.Quantity
        
        # Default prices per board foot (in USD) - approximate market values
        self._default_prices = {
            LumberType.PINE: {
                LumberGrade.SELECT: 4.50,
                LumberGrade.ONE: 3.75,
                LumberGrade.TWO: 3.00,
                LumberGrade.THREE: 2.25,
                LumberGrade.CONSTRUCTION: 2.50,
                LumberGrade.STANDARD: 2.00,
                LumberGrade.UTILITY: 1.75,
                LumberGrade.ECONOMY: 1.50,
                LumberGrade.STUD: 2.25,
                LumberGrade.CUSTOM: 5.00,
            },
            LumberType.FIR: {
                LumberGrade.SELECT: 5.25,
                LumberGrade.ONE: 4.50,
                LumberGrade.TWO: 3.75,
                LumberGrade.THREE: 3.00,
                LumberGrade.CONSTRUCTION: 3.50,
                LumberGrade.STANDARD: 3.25,
                LumberGrade.UTILITY: 2.75,
                LumberGrade.ECONOMY: 2.25,
                LumberGrade.STUD: 3.50,
                LumberGrade.CUSTOM: 6.00,
            },
        }
        
        # Set default prices for other lumber types
        for lumber_type in LumberType:
            if lumber_type not in self._default_prices:
                if lumber_type in [LumberType.OAK, LumberType.MAPLE, LumberType.WALNUT]:
                    # Hardwoods are more expensive
                    self._default_prices[lumber_type] = {
                        grade: price * 2.5 for grade, price in self._default_prices[LumberType.PINE].items()
                    }
                elif lumber_type in [LumberType.CEDAR, LumberType.REDWOOD, LumberType.CYPRESS]:
                    # Outdoor/specialty woods
                    self._default_prices[lumber_type] = {
                        grade: price * 1.75 for grade, price in self._default_prices[LumberType.PINE].items()
                    }
                else:
                    # Other softwoods
                    self._default_prices[lumber_type] = {
                        grade: price * 1.1 for grade, price in self._default_prices[LumberType.PINE].items()
                    }
    
    def calculate_board_feet(
        self,
        nominal_width: Union[int, float, Decimal],
        nominal_thickness: Union[int, float, Decimal],
        length: Union[int, float, Decimal],
        quantity: int = 1,
        length_unit: str = "feet"
    ) -> Dict[str, Union[float, object]]:
        """Calculate board feet for lumber."""
        # Convert nominal dimensions to actual dimensions (standard conversion)
        if nominal_thickness < 2.5:  # 2x lumber
            actual_thickness = 1.5
        elif nominal_thickness < 4.5:  # 4x lumber
            actual_thickness = 3.5
        else:  # 6x or larger
            actual_thickness = nominal_thickness - 0.5
            
        if nominal_width <= 6:
            actual_width = nominal_width - 0.5
        else:
            actual_width = nominal_width - 0.75
        
        # Convert length to feet for board feet calculation
        length_q = self.Q_(float(length), length_unit)
        length_feet = length_q.to(self.ureg.foot).magnitude
        
        # Calculate board feet (width × thickness × length) ÷ 12
        board_feet = (actual_width * actual_thickness * length_feet) / 12 * quantity
        
        # Calculate total actual dimensions
        thickness_q = self.Q_(actual_thickness, 'inch')
        width_q = self.Q_(actual_width, 'inch')
        volume = thickness_q * width_q * length_q * quantity
        
        return {
            "board_feet": round(board_feet, 2),
            "actual_thickness": actual_thickness,
            "actual_width": actual_width,
            "length_feet": length_feet,
            "quantity": quantity,
            "volume": volume,
        }
    
    def calculate_cost(
        self,
        board_feet: Union[float, Dict[str, Union[float, object]]],
        lumber_type: Union[str, LumberType] = LumberType.PINE,
        grade: Union[str, LumberGrade] = LumberGrade.TWO,
        price_per_board_foot: Optional[float] = None
    ) -> float:
        """Calculate cost for lumber."""
        # Extract board feet if a dictionary is provided
        if isinstance(board_feet, dict) and "board_feet" in board_feet:
            board_feet_value = board_feet["board_feet"]
        else:
            board_feet_value = float(board_feet)
        
        # Convert string values to enum if needed
        if isinstance(lumber_type, str):
            lumber_type = LumberType(lumber_type.lower())
        
        if isinstance(grade, str):
            grade = LumberGrade(grade.lower())
        
        # Determine price per board foot
        if price_per_board_foot is not None:
            price = float(price_per_board_foot)
        else:
            price = self._default_prices.get(lumber_type, {}).get(grade, 3.0)
        
        # Calculate total cost
        cost = board_feet_value * price
        
        return round(cost, 2)
    
    def calculate_project(
        self,
        dimensions: List[Tuple[float, float, float, int]],
        lumber_type: Union[str, LumberType] = LumberType.PINE,
        grade: Union[str, LumberGrade] = LumberGrade.TWO,
        length_unit: str = "feet",
        price_per_board_foot: Optional[float] = None,
        waste_factor: float = 0.1  # 10% waste by default
    ) -> Dict[str, Union[float, List[Dict[str, Union[float, object]]]]]:
        """Calculate board feet and cost for a project with multiple lumber pieces."""
        calculations = []
        total_board_feet = 0
        
        for width, thickness, length, quantity in dimensions:
            result = self.calculate_board_feet(
                nominal_width=width,
                nominal_thickness=thickness,
                length=length,
                quantity=quantity,
                length_unit=length_unit
            )
            calculations.append(result)
            total_board_feet += result["board_feet"]
        
        # Apply waste factor
        total_board_feet_with_waste = total_board_feet * (1 + waste_factor)
        
        # Calculate cost
        cost = self.calculate_cost(
            board_feet=total_board_feet_with_waste,
            lumber_type=lumber_type,
            grade=grade,
            price_per_board_foot=price_per_board_foot
        )
        
        return {
            "board_feet": round(total_board_feet, 2),
            "board_feet_with_waste": round(total_board_feet_with_waste, 2),
            "waste_factor": waste_factor,
            "waste_board_feet": round(total_board_feet_with_waste - total_board_feet, 2),
            "cost": cost,
            "lumber_type": lumber_type if isinstance(lumber_type, str) else lumber_type.value,
            "grade": grade if isinstance(grade, str) else grade.value,
            "calculations": calculations,
        }
    
    def get_standard_sizes(self) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        """Get a list of standard lumber sizes."""
        return {
            "dimensional_lumber": [
                {"thickness": 2, "width": 2, "description": "2×2"},
                {"thickness": 2, "width": 3, "description": "2×3"},
                {"thickness": 2, "width": 4, "description": "2×4"},
                {"thickness": 2, "width": 6, "description": "2×6"},
                {"thickness": 2, "width": 8, "description": "2×8"},
                {"thickness": 2, "width": 10, "description": "2×10"},
                {"thickness": 2, "width": 12, "description": "2×12"},
                {"thickness": 4, "width": 4, "description": "4×4"},
                {"thickness": 4, "width": 6, "description": "4×6"},
                {"thickness": 6, "width": 6, "description": "6×6"},
            ],
            "standard_lengths": [
                8, 10, 12, 14, 16, 18, 20, 22, 24
            ],
            "plywood": [
                {"thickness": 0.25, "width": 48, "length": 96, "description": "1/4\" × 4' × 8'"},
                {"thickness": 0.5, "width": 48, "length": 96, "description": "1/2\" × 4' × 8'"},
                {"thickness": 0.75, "width": 48, "length": 96, "description": "3/4\" × 4' × 8'"},
            ],
        }
