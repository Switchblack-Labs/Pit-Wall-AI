"""
Shared engine singleton for backend integration.

Both strategy_engine.py and scenario_engine.py import from here
so models are loaded only once.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_engine.pipeline.strategy_engine import StrategyEngine

_engine = None


def get_engine():
    """Lazy-load and return the shared StrategyEngine singleton."""
    global _engine
    if _engine is None:
        _engine = StrategyEngine()
        _engine.load_models()
    return _engine
