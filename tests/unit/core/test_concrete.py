import pytest
from buildwise.core.concrete import ConcreteCalculator

class TestConcreteCalculator:
    """Test suite for ConcreteCalculator."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.calculator = ConcreteCalculator()
    
    def test_calculate_volume_feet(self):
        """Test volume calculation with feet units."""
        volume = self.calculator.calculate_volume(10, 10, 0.5, "feet")
        assert volume["cubic_yards"] == pytest.approx(1.85, 0.01)
        assert volume["cubic_meters"] == pytest.approx(1.42, 0.01)
    
    def test_calculate_volume_meters(self):
        """Test volume calculation with meter units."""
        volume = self.calculator.calculate_volume(3, 3, 0.15, "meters")
        assert volume["cubic_yards"] == pytest.approx(1.77, 0.01)
        assert volume["cubic_meters"] == pytest.approx(1.35, 0.01)
    
    def test_zero_dimension(self):
        """Test volume calculation with a zero dimension."""
        volume = self.calculator.calculate_volume(0, 10, 0.5, "feet")
        assert volume["cubic_yards"] == 0
        assert volume["cubic_meters"] == 0
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        volume = self.calculator.calculate_volume(10, 10, 0.5, "feet")
        cost = self.calculator.calculate_cost(volume, 150)
        assert cost == pytest.approx(277.5, 0.1)
    
    def test_bags_needed(self):
        """Test bags needed calculation."""
        volume = self.calculator.calculate_volume(10, 10, 0.5, "feet")
        bags = self.calculator.bags_needed(volume, 80, "lb")
        assert bags > 0  # Should be a positive number
        assert isinstance(bags, int)  # Should be an integer
