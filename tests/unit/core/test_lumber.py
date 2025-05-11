"""Tests for the lumber calculator module."""

import pytest
from decimal import Decimal
from buildwise.core.lumber import LumberCalculator, LumberType, LumberGrade


class TestLumberCalculator:
    """Test suite for the lumber calculator."""
    
    def setup_method(self):
        """Set up a calculator instance before each test."""
        self.calculator = LumberCalculator()
    
    def test_calculate_board_feet_2x4(self):
        """Test board feet calculation for 2x4."""
        result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=2,
            length=8,
            quantity=1,
            length_unit="feet"
        )
        
        # Check structure and values
        assert isinstance(result, dict)
        assert "board_feet" in result
        assert "actual_thickness" in result
        assert "actual_width" in result
        
        # A 2x4x8' board should be about 4 board feet
        # (1.5 × 3.5 × 8) ÷ 12 = 3.5
        assert result["board_feet"] == pytest.approx(3.5, 0.01)
        assert result["actual_thickness"] == 1.5
        assert result["actual_width"] == 3.5
    
    def test_calculate_board_feet_4x4(self):
        """Test board feet calculation for 4x4."""
        result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=4,
            length=8,
            quantity=1,
            length_unit="feet"
        )
        
        # A 4x4x8' board should be about 9.33 board feet
        # (3.5 × 3.5 × 8) ÷ 12 = 8.17
        assert result["board_feet"] == pytest.approx(8.17, 0.01)
        assert result["actual_thickness"] == 3.5
        assert result["actual_width"] == 3.5
    
    def test_calculate_board_feet_with_quantity(self):
        """Test board feet calculation with multiple pieces."""
        result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=2,
            length=8,
            quantity=5,
            length_unit="feet"
        )
        
        # 5 pieces of 2x4x8' should be about 17.5 board feet
        # 5 × (1.5 × 3.5 × 8) ÷ 12 = 17.5
        assert result["board_feet"] == pytest.approx(17.5, 0.01)
        assert result["quantity"] == 5
    
    def test_calculate_cost(self):
        """Test cost calculation with default prices."""
        board_feet_result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=2,
            length=8,
            quantity=1,
            length_unit="feet"
        )
        
        cost = self.calculator.calculate_cost(
            board_feet=board_feet_result,
            lumber_type=LumberType.PINE,
            grade=LumberGrade.TWO
        )
        
        # Price should be board_feet × price_per_board_foot
        assert cost > 0
        
        # Test with custom price
        custom_cost = self.calculator.calculate_cost(
            board_feet=board_feet_result,
            price_per_board_foot=5.0
        )
        
        assert custom_cost == pytest.approx(17.5, 0.01)
    
    def test_calculate_project(self):
        """Test project calculation with multiple pieces."""
        dimensions = [
            (4, 2, 8, 10),    # 10 pieces of 2x4x8'
            (6, 2, 10, 6),    # 6 pieces of 2x6x10'
            (12, 2, 16, 2),   # 2 pieces of 2x12x16'
        ]
        
        result = self.calculator.calculate_project(
            dimensions=dimensions,
            lumber_type=LumberType.PINE,
            grade=LumberGrade.TWO,
            waste_factor=0.1
        )
        
        # Check structure and values
        assert isinstance(result, dict)
        assert "board_feet" in result
        assert "board_feet_with_waste" in result
        assert "cost" in result
        assert "calculations" in result
        
        # Check that waste factor is applied correctly
        assert result["board_feet_with_waste"] == pytest.approx(result["board_feet"] * 1.1, 0.01)
        
        # Check that calculations list has the right length
        assert len(result["calculations"]) == len(dimensions)
