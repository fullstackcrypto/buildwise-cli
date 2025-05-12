from enum import Enum

class SteelType(str, Enum):
    REBAR = "rebar"  # Reinforcing bar
    ANGLE = "angle"  # L-shaped cross-section
    CHANNEL = "channel"  # C-shaped cross-section
    I_BEAM = "i_beam"  # I-shaped beam
    WIDE_FLANGE = "wide_flange"  # H-shaped beam (wider flanges than I-beam)
    HSS_RECTANGULAR = "hss_rectangular"  # Hollow Structural Section - rectangular
    HSS_SQUARE = "hss_square"  # Hollow Structural Section - square
    HSS_ROUND = "hss_round"  # Hollow Structural Section - round/pipe
    FLAT_BAR = "flat_bar"  # Rectangular cross-section
    ROUND_BAR = "round_bar"  # Circular cross-section
    SQUARE_BAR = "square_bar"  # Square cross-section
    PLATE = "plate"  # Flat plate
    SHEET = "sheet"  # Thin sheet
    TUBING = "tubing"  # Thin-walled tubing
    PIPE = "pipe"  # Schedule pipe

class SteelGrade(str, Enum):
    A36 = "a36"  # Structural steel (36 ksi yield)
    A53 = "a53"  # Pipe steel
    A500 = "a500"  # HSS steel
    A572_50 = "a572_50"  # High-strength low-alloy (50 ksi yield)
    A992 = "a992"  # Structural steel for wide flange shapes
    A1011 = "a1011"  # Sheet steel
    A1018 = "a1018"  # Plate and bar
    GRADE_40 = "grade_40"  # 40 ksi rebar
    GRADE_60 = "grade_60"  # 60 ksi rebar

class SteelCalculator:
    """Calculator for steel weight and cost estimations."""
    
    def __init__(self):
        """Initialize the calculator."""
        # Standard rebar weights per foot (lb/ft)
        self.rebar_weights = {
            3: 0.376,  # #3 rebar (3/8")
            4: 0.668,  # #4 rebar (1/2")
            5: 1.043,  # #5 rebar (5/8")
            6: 1.502,  # #6 rebar (3/4")
            7: 2.044,  # #7 rebar (7/8")
            8: 2.670,  # #8 rebar (1")
            9: 3.400,  # #9 rebar (1-1/8")
            10: 4.303,  # #10 rebar (1-1/4")
            11: 5.313,  # #11 rebar (1-3/8")
            14: 7.650,  # #14 rebar (1-3/4")
            18: 13.600,  # #18 rebar (2-1/4")
        }
        
        # Default prices per pound for different steel types
        self.price_table = {
            SteelType.REBAR: {
                SteelGrade.GRADE_40: 0.75,
                SteelGrade.GRADE_60: 0.85,
            },
            SteelType.ANGLE: {
                SteelGrade.A36: 0.90,
            },
            # Other steel types and grades would be added here
        }
    
    def calculate_weight(self, steel_type, dimensions, length, quantity=1, 
                         length_unit="feet", weight_unit="pounds"):
        """Calculate steel weight.
        
        Args:
            steel_type (SteelType): Type of steel
            dimensions (dict): Dimensions of the steel section
            length (float): Length of the steel
            quantity (int): Number of pieces
            length_unit (str): Unit for length (feet, meters)
            weight_unit (str): Output weight unit (pounds, kg)
            
        Returns:
            dict: Weight data
        """
        # Convert length to feet if in meters
        if length_unit.lower() == "meters":
            length_feet = length * 3.28084
        else:
            length_feet = length
        
        # Calculate weight based on steel type
        if steel_type == SteelType.REBAR:
            bar_number = dimensions.get("bar_number", 0)
            weight_per_foot = self.rebar_weights.get(bar_number, 0)
            area_sq_inches = self._rebar_area(bar_number)
        elif steel_type == SteelType.ANGLE:
            # L-shaped angle
            width = dimensions.get("width", 0)
            height = dimensions.get("height", 0)
            thickness = dimensions.get("thickness", 0)
            
            # Approximate weight calculation for angle
            area_sq_inches = (width * thickness) + (height * thickness) - (thickness * thickness)
            weight_per_foot = area_sq_inches * 3.4  # Steel is about 3.4 lb/ft³ per square inch
        elif steel_type == SteelType.ROUND_BAR:
            # Round bar
            diameter = dimensions.get("diameter", 0)
            area_sq_inches = 3.14159 * (diameter/2) ** 2
            weight_per_foot = area_sq_inches * 3.4
        else:
            # Generic calculation based on cross-sectional area
            area_sq_inches = dimensions.get("area_sq_inches", 0)
            weight_per_foot = area_sq_inches * 3.4
        
        # Calculate total weight
        weight_pounds = weight_per_foot * length_feet * quantity
        
        # Convert to requested weight unit
        if weight_unit.lower() == "kg" or weight_unit.lower() == "kilograms":
            weight = weight_pounds * 0.453592  # Convert pounds to kg
            weight_unit_output = "kilograms"
        else:
            weight = weight_pounds
            weight_unit_output = "pounds"
        
        return {
            "weight_per_foot": round(weight_per_foot, 2),
            "weight_pounds": round(weight_pounds, 2),
            "weight": round(weight, 2),
            "weight_unit": weight_unit_output,
            "length": length,
            "length_unit": length_unit,
            "quantity": quantity,
            "area_sq_inches": round(area_sq_inches, 2) if area_sq_inches else None,
            "steel_type": steel_type
        }
    
    def calculate_cost(self, weight, steel_type, grade, price_per_pound=None):
        """Calculate steel cost.
        
        Args:
            weight: Weight data from calculate_weight
            steel_type (SteelType): Type of steel
            grade (SteelGrade): Grade of steel
            price_per_pound (float): Custom price per pound
            
        Returns:
            float: Total cost
        """
        if isinstance(weight, dict) and "weight_pounds" in weight:
            weight_pounds = weight["weight_pounds"]
        else:
            weight_pounds = weight
        
        # Use provided price or look up in price table
        if price_per_pound is None:
            # Default values if type or grade not in table
            type_prices = self.price_table.get(steel_type, {SteelGrade.A36: 0.85})
            price = type_prices.get(grade, 0.85)
        else:
            price = price_per_pound
        
        total_cost = weight_pounds * price
        return round(total_cost, 2)
    
    def get_rebar_properties(self, bar_number):
        """Get properties for a specific rebar size.
        
        Args:
            bar_number (int): Rebar size number
            
        Returns:
            dict: Rebar properties
        """
        weight_per_foot = self.rebar_weights.get(bar_number, 0)
        diameter_inches = bar_number / 8.0  # Rebar number is 8 times diameter in inches
        area_sq_inches = self._rebar_area(bar_number)
        
        return {
            "bar_number": bar_number,  # Add this line to make the test pass
            "diameter_inches": diameter_inches,
            "diameter_mm": diameter_inches * 25.4,
            "weight_per_foot": weight_per_foot,
            "weight_per_meter": weight_per_foot * 3.28084,
            "area_sq_inches": area_sq_inches,
            "area_sq_mm": area_sq_inches * 645.16
        }
    
    def _rebar_area(self, bar_number):
        """Calculate cross-sectional area of rebar.
        
        Args:
            bar_number (int): Rebar size number
            
        Returns:
            float: Area in square inches
        """
        diameter_inches = bar_number / 8.0
        return 3.14159 * (diameter_inches/2) ** 2
