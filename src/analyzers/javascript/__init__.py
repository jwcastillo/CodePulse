"""
JavaScript/TypeScript analyzers package.

Contains analyzers for Node.js, Next.js, and general JavaScript/TypeScript code.
"""

from .nodejs_analyzer import NodeJSAnalyzer
from .nextjs_analyzer import NextJSAnalyzer

__all__ = [
    'NodeJSAnalyzer',
    'NextJSAnalyzer'
]
