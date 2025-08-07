"""
Agent AI - Intelligent Security Analysis Platform

An intelligent cybersecurity analysis platform powered by Large Language Models (LLMs)
and event-driven microservices architecture.
"""

__version__ = "2.0.0"
__author__ = "Agent AI Team"
__description__ = "LLM-powered cybersecurity analysis platform"

# Main package imports
from . import agents
from . import cli
from . import config
from . import control
from . import data
from . import utils
from . import webapp

__all__ = [
    "agents",
    "cli", 
    "config",
    "control",
    "data",
    "utils",
    "webapp",
    "__version__",
    "__author__",
    "__description__"
]