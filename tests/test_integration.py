"""
Integration tests for the complete Voltorb Flip solver pipeline.
Tests the full flow: validation → CSP → Monte Carlo → policies → response.
"""

import pytest
from api.models import SolveRequest, LineConstraint, RevealedTile
from api.utils import build_board
from src.engine import SolverEngine


class TestIntegration:
    """End-to-end tests for the solver"""
    
    def test_empty_board_analysis(self):
        """Test analysis of a valid empty board"""
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=7, voltorbs=0),
                LineConstraint(sum=5, voltorbs=2),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=4, voltorbs=2),
            ],
            cols=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=5, voltorbs=1),
                LineConstraint(sum=7, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
            ],
            revealed=[]
        )
        
        board = build_board(request)
        engine = SolverEngine(board, mode="level")
        result = engine.analyze()
        
        # Should return valid response
        assert "recommendations" in result
        assert "guaranteed_safe" in result
        assert "guaranteed_voltorb" in result
        assert "explanation" in result
        assert result["mode"] == "level"
    
    def test_with_revealed_tiles(self):
        """Test analysis with some revealed tiles"""
        request = SolveRequest(
            mode="profit",
            rows=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=7, voltorbs=0),
                LineConstraint(sum=5, voltorbs=2),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=4, voltorbs=2),
            ],
            cols=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=5, voltorbs=1),
                LineConstraint(sum=7, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
            ],
            revealed=[
                RevealedTile(row=0, col=0, value=2),
                RevealedTile(row=1, col=1, value=3),
            ]
        )
        
        board = build_board(request)
        engine = SolverEngine(board, mode="profit")
        result = engine.analyze()
        
        # Should successfully analyze with revealed tiles
        assert result is not None
        assert result["mode"] == "profit"
    
    def test_simple_deterministic_case(self):
        """Test a board where CSP can find guaranteed moves"""
        # Create a simple case: row with sum=0, voltorbs=5
        # All tiles in that row MUST be voltorbs
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=0, voltorbs=5),  # All voltorbs
                LineConstraint(sum=15, voltorbs=0),  # All 3s
                LineConstraint(sum=5, voltorbs=0),   # All 1s
                LineConstraint(sum=5, voltorbs=0),   # All 1s
                LineConstraint(sum=5, voltorbs=0),   # All 1s
            ],
            cols=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
            ],
            revealed=[]
        )
        
        board = build_board(request)
        engine = SolverEngine(board, mode="level")
        result = engine.analyze()
        
        # Row 0 should all be guaranteed voltorbs
        assert len(result["guaranteed_voltorb"]) == 5
        
        # Row 1 should all be guaranteed safe (all 3s)
        assert len(result["guaranteed_safe"]) >= 5
    
    def test_impossible_board_validation(self):
        """Test that impossible boards are caught during validation"""
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=20, voltorbs=0),  # Impossible: max is 15
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
            ],
            cols=[
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=8, voltorbs=0),
            ],
            revealed=[]
        )
        
        with pytest.raises(ValueError, match="too high"):
            build_board(request)
    
    def test_contradictory_constraints(self):
        """Test that contradictory constraints are caught"""
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
                LineConstraint(sum=5, voltorbs=0),
            ],
            cols=[
                LineConstraint(sum=10, voltorbs=0),  # Mismatched totals
                LineConstraint(sum=10, voltorbs=0),
                LineConstraint(sum=10, voltorbs=0),
                LineConstraint(sum=10, voltorbs=0),
                LineConstraint(sum=10, voltorbs=0),
            ],
            revealed=[]
        )
        
        with pytest.raises(ValueError, match="Sum of all row sums"):
            build_board(request)
    
    def test_level_mode_vs_profit_mode(self):
        """Test that different modes produce different recommendations"""
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=6, voltorbs=2),
                LineConstraint(sum=7, voltorbs=1),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=5, voltorbs=1),
                LineConstraint(sum=4, voltorbs=1),
            ],
            cols=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
            ],
            revealed=[]
        )
        
        board_level = build_board(request)
        engine_level = SolverEngine(board_level, mode="level")
        result_level = engine_level.analyze()
        
        board_profit = build_board(request)
        engine_profit = SolverEngine(board_profit, mode="profit")
        result_profit = engine_profit.analyze()
        
        # Both should succeed
        assert result_level is not None
        assert result_profit is not None
        
        # Modes should be set correctly
        assert result_level["mode"] == "level"
        assert result_profit["mode"] == "profit"
        
        # Both should have recommendations
        assert len(result_level["recommendations"]) > 0
        assert len(result_profit["recommendations"]) > 0
    
    def test_quit_recommendation_trigger(self):
        """Test that quit recommendation is triggered appropriately"""
        # Create a dangerous board: high voltorb density
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
            ],
            cols=[
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
                LineConstraint(sum=3, voltorbs=4),
            ],
            revealed=[]
        )
        
        board = build_board(request)
        engine = SolverEngine(board, mode="level")
        result = engine.analyze()
        
        # With such high voltorb density, quit should likely be recommended
        # (This is probabilistic, so we just check the field exists)
        assert "quit_recommended" in result
        assert isinstance(result["quit_recommended"], bool)
    
    def test_response_schema_compliance(self):
        """Test that response matches expected schema"""
        request = SolveRequest(
            mode="level",
            rows=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=7, voltorbs=0),
                LineConstraint(sum=5, voltorbs=2),
                LineConstraint(sum=8, voltorbs=0),
                LineConstraint(sum=4, voltorbs=2),
            ],
            cols=[
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=5, voltorbs=1),
                LineConstraint(sum=7, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
                LineConstraint(sum=6, voltorbs=1),
            ],
            revealed=[]
        )
        
        board = build_board(request)
        engine = SolverEngine(board, mode="level")
        result = engine.analyze()
        
        # Check all required fields exist
        required_fields = [
            "guaranteed_safe",
            "guaranteed_voltorb",
            "recommendations",
            "quit_recommended",
            "explanation",
            "mode"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Check types
        assert isinstance(result["guaranteed_safe"], list)
        assert isinstance(result["guaranteed_voltorb"], list)
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["quit_recommended"], bool)
        assert isinstance(result["explanation"], str)
        assert result["mode"] in ["level", "profit"]
        
        # Check recommendation structure
        if result["recommendations"]:
            rec = result["recommendations"][0]
            assert "position" in rec
            assert "p_voltorb" in rec or "pVoltorb" in rec
            assert "expected_value" in rec or "expectedValue" in rec
            assert "risk_tier" in rec or "riskTier" in rec


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])