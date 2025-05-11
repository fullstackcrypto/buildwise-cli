"""Tests for the steel calculator module."""

import pytest
from decimal import Decimal
from buildwise.core.steel import SteelCalculator, SteelType, SteelGrade


class TestSteelCalculator:
    """Test suite for the steel calculator."""
    
    def setup_method(self):
        """Set up a calculator instance before each test."""
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
        
        # Check structure and values
        assert isinstance(result, dict)
        assert "weight_pounds" in result
        assert "weight_per_foot" in result
        
        # A #4 rebar should be about 0.668 lb per foot
        # Total for 10 feet should be around 6.68 lb
        assert result["weight_per_foot"] == pytest.approx(0.668, 0.1)
        assert result["weight_pounds"] == pytest.approx(6.68, 0.1)
    
    def test_calculate_weight_angle(self):
        """Test weight calculation for angle iron."""
        result = self.calculator.calculate_weight(
            steel_type=SteelType.ANGLE,
            dimensions={"width": 3, "height": 3, "thickness": 0.25},
            length=10,
            quantity=1,
            length_unit="feet"
        )
        
        # Check that weight is reasonable for a 3x3x1/4 angle (around 7.7 lb/ft)
        assert result["weight_per_foot"] > 7
        assert result["weight_per_foot"] < 8
        assert result["weight_pounds"] == pytest.approx(result["weight_per_foot"] * 10, 0.1)
    
    def test_calculate_weight_round_tube(self):
        """Test weight calculation for round tube."""
        result = self.calculator.calculate_weight(
            steel_type=SteelType.HSS_ROUND,
            dimensions={"diameter": 4, "wall_thickness": 0.25},
            length=12,
            quantity=1,
            length_unit="feet"
        )
        
        # Check values
        assert "weight_pounds" in result
        assert "area_sq_inches" in result
        assert result["weight_pounds"] > 0
    
    def test_calculate_weight_with_metric_units(self):
        """Test weight calculation with metric units."""
        result = self.calculator.calculate_weight(
            steel_type=SteelType.FLAT_BAR,
            dimensions={"width": 50, "thickness": 10},  # mm
            length=3,  # meters
            quantity=1,
            length_unit="meters",
            dimension_unit="mm",
            weight_unit="kg"
        )
        
        # Check that output is in kg
        assert result["weight_unit"] == "kg"
        assert result["weight"] > 0
    
    def test_calculate_cost(self):
        """Test cost calculation for steel."""
        weight_result = self.calculator.calculate_weight(
            steel_type=SteelType.REBAR,
            dimensions={"bar_number": 5},
            length=100,
            quantity=1
        )
        
        cost = self.calculator.calculate_cost(
            weight=weight_result,
            steel_type=SteelType.REBAR,
            grade=SteelGrade.GRADE_60
        )
        
        # Check that cost is calculated correctly
        # #5 rebar is about 1.04 lb/ft, so 100 ft = 104 lb
        # Grade 60 rebar price is about $0.75/lb, so cost should be around $78
        assert cost > 70
        assert cost < 85
        
        # Test with custom price
        custom_cost = self.calculator.calculate_cost(
            weight=weight_result,
            price_per_pound=1.0
        )
        
        # Custom price of $1/lb should result in cost equal to weight
        assert custom_cost == pytest.approx(weight_result["weight_pounds"], 0.1)
    
    def test_rebar_properties(self):
        """Test getting rebar properties."""
        # Test for #5 rebar
        props = self.calculator.get_rebar_properties(5)
        
        assert "diameter" in props
        assert "weight_per_foot" in props
        assert "area_sq_inches" in props
        assert props["diameter"] == 0.625  # #5 = 5/8"
        assert props["weight_per_foot"] == pytest.approx(1.043, 0.01)
        
        # Test with invalid bar number (should return #4 properties)
        default_props = self.calculator.get_rebar_properties(99)
        assert default_props["diameter"] == 0.5  # #4 = 1/2"
    
    def test_standard_shapes(self):
        """Test getting standard shapes."""
        shapes = self.calculator.get_standard_shapes()
        
        # Check structure
        assert "rebar" in shapes
        assert "angle" in shapes
        assert "wide_flange" in shapes
        
        # Check filtering by type
        rebar_only = self.calculator.get_standard_shapes(SteelType.REBAR)
        assert "rebar" in rebar_only
        assert len(rebar_only) == 1
