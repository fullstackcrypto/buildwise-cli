from enum import Enum
import math

class LumberType(str, Enum):
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
    """Calculator for lumber measurements and cost estimation."""
    
    def __init__(self):
        # Nominal to actual dimension mappings
        self.dimension_map = {
            # thickness (nominal -> actual)
            "thickness": {
                2: 1.5,
                3: 2.5,
                4: 3.5,
                6: 5.5,
                8: 7.25,
                10: 9.25,
                12: 11.25
            },
            # width (nominal -> actual)
            "width": {
                2: 1.5,
                3: 2.5,
                4: 3.5,
                6: 5.5,
                8: 7.25,
                10: 9.25,
                12: 11.25
            }
        }
        
        # Default prices per board foot by lumber type and grade
        self.price_table = {
            LumberType.PINE: {
                LumberGrade.SELECT: 6.0,
                LumberGrade.ONE: 4.5,
                LumberGrade.TWO: 3.0,
                LumberGrade.THREE: 2.5,
                LumberGrade.CONSTRUCTION: 3.2,
                LumberGrade.STANDARD: 2.8,
                LumberGrade.UTILITY: 2.3,
                LumberGrade.ECONOMY: 2.0,
                LumberGrade.STUD: 2.6,
                LumberGrade.CUSTOM: 5.0
            },
            # Add more lumber types as needed...
        }
        
        # Set default prices for other lumber types
        for lumber_type in LumberType:
            if lumber_type not in self.price_table:
                self.price_table[lumber_type] = self.price_table[LumberType.PINE].copy()
        
        # Adjust prices for other lumber types
        self._adjust_prices()
    
    def _adjust_prices(self):
        """Adjust prices for different lumber types."""
        # Multipliers for different lumber types relative to pine
        multipliers = {
            LumberType.FIR: 1.2,
            LumberType.CEDAR: 1.5,
            LumberType.OAK: 2.5,
            LumberType.MAPLE: 2.8,
            LumberType.WALNUT: 3.5,
            LumberType.REDWOOD: 2.0,
            LumberType.SPRUCE: 1.1,
            LumberType.CYPRESS: 1.8,
            LumberType.POPLAR: 1.3
        }
        
        # Apply multipliers
        for lumber_type, multiplier in multipliers.items():
            if lumber_type in self.price_table:
                for grade in self.price_table[lumber_type]:
                    self.price_table[lumber_type][grade] *= multiplier
    
    def calculate_board_feet(self, nominal_width, nominal_thickness, length, quantity=1, length_unit="feet"):
        """Calculate board feet for given lumber dimensions.
        
        Args:
            nominal_width: Nominal width in inches (e.g., 4 for a 2x4)
            nominal_thickness: Nominal thickness in inches (e.g., 2 for a 2x4)
            length: Length of the lumber
            quantity: Number of pieces
            length_unit: Unit for length (feet or meters)
            
        Returns:
            dict: Board feet calculation results
        """
        # Convert length to feet if necessary
        length_feet = length
        if length_unit == "meters":
            length_feet = length * 3.28084
        
        # Get actual dimensions
        actual_thickness = self.dimension_map["thickness"].get(nominal_thickness, nominal_thickness)
        actual_width = self.dimension_map["width"].get(nominal_width, nominal_width)
        
        # Calculate board feet: (thickness * width * length) / 12
        board_feet = (actual_thickness * actual_width * length_feet * quantity) / 12
        
        return {
            "board_feet": board_feet,
            "actual_thickness": actual_thickness,
            "actual_width": actual_width,
            "length_feet": length_feet,
            "quantity": quantity,
            "volume": {
                "cubic_inches": actual_thickness * actual_width * length_feet * 12 * quantity,
                "cubic_feet": (actual_thickness * actual_width * length_feet * quantity) / 144
            }
        }
    
    def calculate_cost(self, board_feet, lumber_type=LumberType.PINE, grade=LumberGrade.TWO, price_per_board_foot=None):
        """Calculate cost based on board feet.
        
        Args:
            board_feet: Board feet value or result dict from calculate_board_feet
            lumber_type: Type of lumber
            grade: Grade of lumber
            price_per_board_foot: Custom price (will use default if None)
            
        Returns:
            float: Total cost
        """
        # Extract board feet if a dict was provided
        bf = board_feet
        if isinstance(board_feet, dict) and "board_feet" in board_feet:
            bf = board_feet["board_feet"]
        
        # Get price per board foot
        price = price_per_board_foot
        if price is None:
            # Use default price from table
            price = self.price_table.get(lumber_type, {}).get(grade, 3.0)
        
        # Calculate cost
        cost = bf * price
        return cost
    
    def calculate_project(self, dimensions, lumber_type=LumberType.PINE, grade=LumberGrade.TWO, waste_factor=0.1):
        """Calculate lumber requirements for a project with multiple pieces.
        
        Args:
            dimensions: List of tuples (width, thickness, length, quantity)
            lumber_type: Type of lumber
            grade: Grade of lumber
            waste_factor: Waste factor (0.1 = 10%)
            
        Returns:
            dict: Project calculation results
        """
        total_board_feet = 0
        pieces = []
        
        for dimension in dimensions:
            width, thickness, length, quantity = dimension
            result = self.calculate_board_feet(width, thickness, length, quantity)
            total_board_feet += result["board_feet"]
            pieces.append({
                "dimensions": f"{thickness}x{width}x{length}'",
                "quantity": quantity,
                "board_feet": result["board_feet"]
            })
        
        # Apply waste factor
        total_with_waste = total_board_feet * (1 + waste_factor)
        
        # Calculate cost
        cost = self.calculate_cost(total_with_waste, lumber_type, grade)
        
        return {
            "total_board_feet": total_board_feet,
            "waste_factor": waste_factor,
            "total_with_waste": total_with_waste,
            "cost": cost,
            "pieces": pieces
        }
    
    def get_lumber_info(self, nominal_thickness, nominal_width, length):
        """Get information about a lumber piece.
        
        Args:
            nominal_thickness: Nominal thickness in inches
            nominal_width: Nominal width in inches
            length: Length in feet
            
        Returns:
            dict: Lumber information
        """
        result = self.calculate_board_feet(nominal_width, nominal_thickness, length)
        
        info = {
            "nominal_size": f"{nominal_thickness}x{nominal_width}x{length}'",
            "actual_size": f"{result['actual_thickness']}\"x{result['actual_width']}\"x{length}'",
            "board_feet": result["board_feet"],
            "weight_lbs": result["board_feet"] * 2.5  # Approximate weight
        }
        
        return info
    
    def get_default_price(self, lumber_type, grade):
        """Get default price for lumber type and grade."""
        # This would normally call an API, but we'll simulate it for now
        return self.price_table.get(lumber_type, {}).get(grade, 3.0)
