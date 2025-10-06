"""
Core package for CodePulse analyzer.

This package contains the fundamental building blocks used by all analyzers.
"""

from .models import (
    Issue,
    Pattern,
    AnalysisResult,
    Severity,
    Category
)
from .base_analyzer import BaseAnalyzer

__all__ = [
    'Issue',
    'Pattern',
    'AnalysisResult',
    'Severity',
    'Category',
    'BaseAnalyzer'
]
