"""MechForge AI Self-Reflection System.

This module provides AI self-reflection capabilities for continuous improvement.
It enables recording interactions, analyzing errors, extracting lessons, and
applying learned knowledge to future tasks.

Example:
    >>> from mechforge_core.reflection import ReflectionLogger, ReflectionEngine
    >>> logger = ReflectionLogger()
    >>> log_id = logger.log_interaction(
    ...     task="Code review",
    ...     input="Review this Python function",
    ...     output="The function looks good",
    ...     result="partial",
    ...     feedback="Missed a potential bug"
    ... )
    >>> engine = ReflectionEngine()
    >>> reflection = engine.reflect_on_task(log_id)
"""

from .models import (
    InteractionLog, 
    ReflectionEntry, 
    Lesson, 
    ErrorType,
    ReflectionConfig,
    TaskResult
)
from .logger import ReflectionLogger
from .engine import ReflectionEngine
from .experience_db import ExperienceDB
from .reporter import ReflectionReporter

__all__ = [
    "InteractionLog",
    "ReflectionEntry",
    "Lesson",
    "ErrorType",
    "ReflectionConfig",
    "TaskResult",
    "ReflectionLogger",
    "ReflectionEngine",
    "ExperienceDB",
    "ReflectionReporter",
]

__version__ = "0.1.0"
