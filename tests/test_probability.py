from src.probability.metrics import ProbabilityMetrics


def test_voltorb_probability():
    dist = {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
    assert ProbabilityMetrics.voltorb_probability(dist) == 0.25


def test_expected_value():
    dist = {0: 0.1, 1: 0.3, 2: 0.4, 3: 0.2}
    ev = ProbabilityMetrics.expected_value(dist)
    assert abs(ev - (1*0.3 + 2*0.4 + 3*0.2)) < 1e-6


def test_risk_tiers():
    assert ProbabilityMetrics.risk_tier(0.0) == "GUARANTEED_SAFE"
    assert ProbabilityMetrics.risk_tier(0.1) == "LOW_RISK"
    assert ProbabilityMetrics.risk_tier(0.25) == "MEDIUM_RISK"
    assert ProbabilityMetrics.risk_tier(0.6) == "HIGH_RISK"
