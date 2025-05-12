import pytest
from buildwise.core.lumber import LumberCalculator, LumberType, LumberGrade

class TestLumberCalculator:
    """Test suite for LumberCalculator."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.calculator = LumberCalculator()
    
    def test_calculate_board_feet(self):
        """Test board feet calculation."""
        result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=2,
            length=8,
            quantity=1,
            length_unit="feet"
        )
        assert "board_feet" in result
        assert result["board_feet"] == pytest.approx(3.5, 0.01)
        assert result["actual_thickness"] == 1.5
        assert result["actual_width"] == 3.5
    
    def test_nominal_to_actual_conversion(self):
        """Test nominal to actual dimension conversion."""
        # Standard 2x4
        result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=2,
            length=8
        )
        assert result["actual_thickness"] == 1.5
        assert result["actual_width"] == 3.5
        
        # Standard 2x6
        result = self.calculator.calculate_board_feet(
            nominal_width=6,
            nominal_thickness=2,
            length=8
        )
        assert result["actual_thickness"] == 1.5
        assert result["actual_width"] == 5.5
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        result = self.calculator.calculate_board_feet(
            nominal_width=4,
            nominal_thickness=2,
            length=8,
            quantity=1
        )
        cost = self.calculator.calculate_cost(
            board_feet=result,
            lumber_type=LumberType.PINE,
            grade=LumberGrade.TWO
        )
        assert cost > 0
    
    def test_calculate_project(self):
        """Test project calculation."""
        dimensions = [
            (4, 2, 8, 10),  # 10 pieces of 2x4x8'
            (6, 2, 10, 5),   # 5 pieces of 2x6x10'
        ]
        result = self.calculator.calculate_project(
            dimensions=dimensions,
            lumber_type=LumberType.PINE,
            grade=LumberGrade.TWO,
            waste_factor=0.1
        )
        assert "total_board_feet" in result
        assert "total_with_waste" in result
        assert result["total_with_waste"] > result["total_board_feet"]
        assert len(result["pieces"]) == 2
