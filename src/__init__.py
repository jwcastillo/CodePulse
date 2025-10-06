"""
CodePulse - Advanced Code Quality Analysis Tool
"""

__version__ = "2.0.0"

from .core import (
    Issue,
    Pattern,
    AnalysisResult,
    Severity,
    Category,
    BaseAnalyzer
)

__all__ = [
    '__version__',
    'Issue',
    'Pattern',
    'AnalysisResult',
    'Severity',
    'Category',
    'BaseAnalyzer'
]
