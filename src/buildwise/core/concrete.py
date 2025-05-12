"""Concrete calculator module for BuildWise CLI."""

from decimal import Decimal
from typing import Dict, Union

from pint import UnitRegistry

# Initialize unit registry with default definitions
ureg = UnitRegistry()


class ConcreteCalculator:
    """Calculator for concrete volume and cost estimation."""

    def __init__(self):
        """Initialize the concrete calculator."""
        self.ureg = UnitRegistry()
        self.Q_ = self.ureg.Quantity

    def calculate_volume(
        self,
        length: Union[int, float, Decimal],
        width: Union[int, float, Decimal],
        depth: Union[int, float, Decimal],
        unit: str = "feet",
    ) -> Dict[str, Union[float, object]]:
        """Calculate concrete volume.

        Args:
            length: Length of the area
            width: Width of the area
            depth: Depth of the concrete
            unit: Unit of measurement (feet, meters, inches, etc.)

        Returns:
            Dict containing volume in cubic yards and cubic meters, plus raw volume
        """
        # Create quantities with units
        length_q = self.Q_(float(length), unit)
        width_q = self.Q_(float(width), unit)
        depth_q = self.Q_(float(depth), unit)

        # Calculate volume
        volume = length_q * width_q * depth_q

        # Convert to standard units - using unit**3 format instead of cubic_unit
        cubic_yards = volume.to(self.ureg.yard**3).magnitude
        cubic_meters = volume.to(self.ureg.meter**3).magnitude

        return {
            "cubic_yards": round(cubic_yards, 2),
            "cubic_meters": round(cubic_meters, 2),
            "raw_volume": volume,
        }

    def calculate_cost(
        self,
        volume: Union[Dict[str, Union[float, object]], object],
        price_per_unit: Union[int, float, Decimal],
        unit: str = "cubic_yard",
    ) -> float:
        """Calculate concrete cost.

        Args:
            volume: Volume object from calculate_volume or raw Pint quantity
            price_per_unit: Price per unit volume
            unit: Unit for pricing (cubic_yard, cubic_meter)

        Returns:
            Total cost
        """
        # Extract raw volume if dictionary is provided
        if isinstance(volume, dict) and "raw_volume" in volume:
            volume = volume["raw_volume"]

        # Convert to target unit and calculate cost
        if unit == "cubic_yard":
            volume_in_unit = volume.to(self.ureg.yard**3).magnitude
        elif unit == "cubic_meter":
            volume_in_unit = volume.to(self.ureg.meter**3).magnitude
        else:
            raise ValueError(f"Unsupported unit: {unit}")

        cost = float(price_per_unit) * volume_in_unit

        return round(cost, 2)

    def bags_needed(
        self,
        volume: Dict[str, Union[float, object]],
        bag_size: Union[int, float, Decimal] = 80,
        bag_unit: str = "lb",
    ) -> int:
        """Calculate number of bags needed.

        Args:
            volume: Volume object from calculate_volume
            bag_size: Size of the bag (default: 80)
            bag_unit: Unit for bag size (lb, kg)

        Returns:
            Number of bags needed
        """
        # Standard coverage:
        # - 80 lb bag = 0.6 cubic feet
        # - 60 lb bag = 0.45 cubic feet
        # - 50 kg bag = 0.5 cubic feet

        if bag_unit == "lb":
            if bag_size == 80:
                coverage_cuft = 0.6
            elif bag_size == 60:
                coverage_cuft = 0.45
            else:
                coverage_cuft = (float(bag_size) / 80) * 0.6
        elif bag_unit == "kg":
            if bag_size == 50:
                coverage_cuft = 0.5
            else:
                coverage_cuft = (float(bag_size) / 50) * 0.5

        # Get volume in cubic feet
        raw_volume = volume["raw_volume"]
        volume_cuft = raw_volume.to(self.ureg.foot**3).magnitude

        # Calculate bags and round up
        import math

        bags = math.ceil(volume_cuft / coverage_cuft)

        return bags
