"""Tests for the concrete calculator module."""

import pytest
from decimal import Decimal
from buildwise.core.concrete import ConcreteCalculator


class TestConcreteCalculator:
    """Test suite for the concrete calculator."""
    
    def setup_method(self):
        """Set up a calculator instance before each test."""
        self.calculator = ConcreteCalculator()
    
    def test_calculate_volume_with_feet(self):
        """Test volume calculation with feet units."""
        volume = self.calculator.calculate_volume(10, 10, 0.5, "feet")
        
        # Check structure and values
        assert isinstance(volume, dict)
        assert "cubic_yards" in volume
        assert "cubic_meters" in volume
        assert "raw_volume" in volume
        assert volume["cubic_yards"] == pytest.approx(1.85, 0.01)
        assert volume["cubic_meters"] == pytest.approx(1.42, 0.01)
    
    def test_calculate_volume_with_meters(self):
        """Test volume calculation with meter units."""
        volume = self.calculator.calculate_volume(3, 3, 0.15, "meters")
        
        assert volume["cubic_yards"] == pytest.approx(1.77, 0.01)
        assert volume["cubic_meters"] == pytest.approx(1.35, 0.01)
    
    def test_volume_with_decimal_inputs(self):
        """Test volume calculation with Decimal inputs."""
        volume = self.calculator.calculate_volume(
            Decimal("10.5"), 
            Decimal("10.25"), 
            Decimal("0.45"),
            "feet"
        )
        
        assert isinstance(volume["cubic_yards"], float)
        assert volume["cubic_yards"] > 0
    
    def test_calculate_cost(self):
        """Test cost calculation with a price per cubic yard."""
        volume = self.calculator.calculate_volume(10, 10, 0.5, "feet")
        cost = self.calculator.calculate_cost(volume, 150)
        
        assert cost == pytest.approx(277.5, 0.1)
    
    def test_bags_needed(self):
        """Test calculation of bags needed."""
        volume = self.calculator.calculate_volume(10, 10, 0.5, "feet")
        
        # 80 lb bags
        bags_80lb = self.calculator.bags_needed(volume, 80, "lb")
        assert bags_80lb > 0
        assert isinstance(bags_80lb, int)
        
        # 50 kg bags
        bags_50kg = self.calculator.bags_needed(volume, 50, "kg")
        assert bags_50kg > 0
        assert isinstance(bags_50kg, int)
        
        # Check that smaller bags require more units
        bags_60lb = self.calculator.bags_needed(volume, 60, "lb")
        assert bags_60lb > bags_80lb
