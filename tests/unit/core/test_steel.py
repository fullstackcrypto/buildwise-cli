import pytest
from buildwise.core.steel import SteelCalculator, SteelType, SteelGrade

class TestSteelCalculator:
    """Test suite for SteelCalculator."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.calculator = SteelCalculator()
    
    def test_calculate_weight_rebar(self):
        """Test weight calculation for rebar."""
        result = self.calculator.calculate_weight(
            steel_type=SteelType.REBAR,
            dimensions={"bar_number": 4},
            length=10,
            quantity=1,
            length_unit="feet"
        )
        assert result["weight_pounds"] == pytest.approx(6.68, 0.01)
        assert result["weight_per_foot"] == pytest.approx(0.668, 0.01)
    
    def test_calculate_weight_angle(self):
        """Test weight calculation for angle."""
        result = self.calculator.calculate_weight(
            steel_type=SteelType.ANGLE,
            dimensions={"width": 3, "height": 3, "thickness": 0.25},
            length=10,
            quantity=1,
            length_unit="feet"
        )
        assert "weight_pounds" in result
        assert result["weight_pounds"] > 0
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        result = self.calculator.calculate_weight(
            steel_type=SteelType.REBAR,
            dimensions={"bar_number": 4},
            length=10,
            quantity=1
        )
        cost = self.calculator.calculate_cost(
            weight=result,
            steel_type=SteelType.REBAR,
            grade=SteelGrade.GRADE_60
        )
        assert cost > 0
    
    def test_get_rebar_properties(self):
        """Test getting rebar properties."""
        props = self.calculator.get_rebar_properties(5)
        assert props["bar_number"] == 5
        assert props["diameter_inches"] == pytest.approx(0.625, 0.01)
        assert props["weight_per_foot"] == pytest.approx(1.043, 0.01)
