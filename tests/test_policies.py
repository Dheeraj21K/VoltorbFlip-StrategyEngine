from src.policies.level import LevelMaximizationPolicy
from src.policies.profit import ProfitMaximizationPolicy
from src.policies.quit import QuitPolicy


def test_level_policy_ranking():
    metrics = {
        (0, 0): {"p_voltorb": 0.1, "expected_value": 1.0, "risk_tier": "LOW_RISK"},
        (0, 1): {"p_voltorb": 0.3, "expected_value": 2.0, "risk_tier": "MEDIUM_RISK"},
        (0, 2): {"p_voltorb": 0.05, "expected_value": 1.0, "risk_tier": "LOW_RISK"},
    }

    policy = LevelMaximizationPolicy(required_safe_moves=1)
    recs = policy.recommend(metrics)

    # Lowest risk should be first
    assert recs[0][0] == (0, 2)


def test_profit_policy_scoring():
    metrics = {
        (1, 1): {"p_voltorb": 0.2, "expected_value": 2.5, "risk_tier": "MEDIUM_RISK"},
        (1, 2): {"p_voltorb": 0.1, "expected_value": 1.8, "risk_tier": "LOW_RISK"},
    }

    policy = ProfitMaximizationPolicy(risk_penalty=1.0)
    recs = policy.recommend(metrics, top_k=1)

    # First tile should have higher EV-risk score
    assert recs[0][0] == (1, 1)


def test_quit_policy_level_mode():
    quit_policy = QuitPolicy(survival_threshold=0.6)

    assert quit_policy.should_quit_level_mode(0.4) is True
    assert quit_policy.should_quit_level_mode(0.8) is False

