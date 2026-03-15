"""Integration utilities for the reflection system.

This module provides easy integration points for using the reflection
system within MechForge AI components.
"""

import functools
import time
from typing import Any, Callable, Optional, TypeVar

from .engine import ReflectionEngine
from .logger import ReflectionLogger
from .models import TaskResult

T = TypeVar("T")


class ReflectionMixin:
    """Mixin class for adding reflection capabilities to other classes.
    
    This mixin provides easy integration of reflection logging and
    analysis into any class that performs tasks.
    
    Example:
        >>> class MyService(ReflectionMixin):
        ...     def __init__(self):
        ...         super().__init__()
        ...     
        ...     def process(self, input_data):
        ...         with self.reflect_task("process_data", input_data):
        ...             # Do processing
        ...             return result
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reflection_logger = None
        self._reflection_engine = None
        
    @property
    def reflection_logger(self) -> ReflectionLogger:
        """Get or create the reflection logger."""
        if self._reflection_logger is None:
            self._reflection_logger = ReflectionLogger()
        return self._reflection_logger
    
    @property
    def reflection_engine(self) -> ReflectionEngine:
        """Get or create the reflection engine."""
        if self._reflection_engine is None:
            self._reflection_engine = ReflectionEngine()
        return self._reflection_engine
    
    def reflect_task(
        self,
        task_description: str,
        user_input: str,
        task_type: str = "general",
        auto_reflect: bool = True,
    ):
        """Context manager for logging and reflecting on a task.
        
        Args:
            task_description: Description of the task
            user_input: Input to the task
            task_type: Type of task
            auto_reflect: Whether to auto-reflect on failure
            
        Returns:
            ReflectionContext context manager
        """
        return ReflectionContext(
            self.reflection_logger,
            self.reflection_engine,
            task_description,
            user_input,
            task_type,
            auto_reflect,
        )
    
    def log_success(
        self,
        task_description: str,
        user_input: str,
        ai_output: str,
        task_type: str = "general",
        **kwargs
    ):
        """Log a successful task."""
        return self.reflection_logger.log_interaction(
            task_description=task_description,
            user_input=user_input,
            ai_output=ai_output,
            result="success",
            task_type=task_type,
            **kwargs
        )
    
    def log_failure(
        self,
        task_description: str,
        user_input: str,
        ai_output: str,
        feedback: Optional[str] = None,
        task_type: str = "general",
        auto_reflect: bool = True,
        **kwargs
    ):
        """Log a failed task and optionally trigger reflection."""
        log_id = self.reflection_logger.log_interaction(
            task_description=task_description,
            user_input=user_input,
            ai_output=ai_output,
            result="failure",
            user_feedback=feedback,
            task_type=task_type,
            **kwargs
        )
        
        if auto_reflect:
            log = self.reflection_logger.get_log(log_id)
            self.reflection_engine.reflect_on_task(log)
            
        return log_id


class ReflectionContext:
    """Context manager for task reflection.
    
    This context manager handles logging task start, capturing output,
    and triggering reflection based on success/failure.
    
    Example:
        >>> with ReflectionContext(logger, engine, "task", "input") as ctx:
        ...     result = do_something()
        ...     ctx.set_output(result)
    """
    
    def __init__(
        self,
        logger: ReflectionLogger,
        engine: ReflectionEngine,
        task_description: str,
        user_input: str,
        task_type: str = "general",
        auto_reflect: bool = True,
    ):
        self.logger = logger
        self.engine = engine
        self.task_description = task_description
        self.user_input = user_input
        self.task_type = task_type
        self.auto_reflect = auto_reflect
        
        self.log_id = None
        self.output = None
        self.start_time = None
        self.success = None
        
    def __enter__(self):
        """Enter the context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and log the result."""
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_type is not None:
            # Exception occurred - log as failure
            self.success = False
            result = "failure"
            output = self.output or f"Exception: {exc_val}"
        else:
            # Success
            self.success = True
            result = "success"
            output = self.output or "Task completed"
        
        self.log_id = self.logger.log_interaction(
            task_description=self.task_description,
            user_input=self.user_input,
            ai_output=output,
            result=result,
            task_type=self.task_type,
            duration_ms=duration_ms,
        )
        
        # Auto-reflect on failure
        if not self.success and self.auto_reflect:
            log = self.logger.get_log(self.log_id)
            self.engine.reflect_on_task(log)
        
        # Don't suppress exceptions
        return False
    
    def set_output(self, output: str):
        """Set the task output."""
        self.output = output


def with_reflection(
    task_description: Optional[str] = None,
    task_type: str = "general",
    auto_reflect: bool = True,
):
    """Decorator for adding reflection to functions.
    
    This decorator automatically logs function calls and their results,
    and can trigger reflection on failures.
    
    Args:
        task_description: Description of the task (defaults to function name)
        task_type: Type of task
        auto_reflect: Whether to auto-reflect on failure
        
    Returns:
        Decorated function
        
    Example:
        >>> @with_reflection(task_type="coding")
        ... def generate_code(prompt):
        ...     return ai.generate(prompt)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            desc = task_description or func.__name__
            input_str = f"args={args}, kwargs={kwargs}"
            
            logger = ReflectionLogger()
            engine = ReflectionEngine()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                output_str = str(result)[:500]  # Limit output length
                
                log_id = logger.log_interaction(
                    task_description=desc,
                    user_input=input_str,
                    ai_output=output_str,
                    result="success",
                    task_type=task_type,
                    duration_ms=duration_ms,
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                log_id = logger.log_interaction(
                    task_description=desc,
                    user_input=input_str,
                    ai_output=f"Exception: {str(e)}",
                    result="failure",
                    task_type=task_type,
                    duration_ms=duration_ms,
                )
                
                if auto_reflect:
                    log = logger.get_log(log_id)
                    engine.reflect_on_task(log)
                
                raise
        
        return wrapper
    return decorator


class ReflectionAwareLLM:
    """Wrapper for LLM clients that integrates reflection.
    
    This wrapper enhances LLM calls with reflection capabilities,
    automatically logging interactions and applying learned lessons.
    
    Example:
        >>> llm = ReflectionAwareLLM(openai_client)
        >>> response = llm.generate("How to optimize Python code?")
        >>> # Interaction is automatically logged
    """
    
    def __init__(self, llm_client, task_type: str = "llm"):
        """Initialize the wrapper.
        
        Args:
            llm_client: The underlying LLM client
            task_type: Type of LLM tasks
        """
        self.llm_client = llm_client
        self.task_type = task_type
        self.logger = ReflectionLogger()
        self.engine = ReflectionEngine()
        
    def generate(
        self,
        prompt: str,
        enhance_with_lessons: bool = True,
        **kwargs
    ) -> str:
        """Generate a response with reflection integration.
        
        Args:
            prompt: The input prompt
            enhance_with_lessons: Whether to enhance prompt with lessons
            **kwargs: Additional arguments for the LLM
            
        Returns:
            Generated response
        """
        # Enhance prompt with relevant lessons
        if enhance_with_lessons:
            enhanced_prompt = self.engine.enhance_prompt_with_reflections(
                prompt,
                prompt,
            )
        else:
            enhanced_prompt = prompt
        
        start_time = time.time()
        
        try:
            # Call the underlying LLM
            response = self.llm_client.generate(enhanced_prompt, **kwargs)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log the interaction
            self.logger.log_interaction(
                task_description="LLM generation",
                user_input=prompt,
                ai_output=response[:500],
                result="success",
                task_type=self.task_type,
                duration_ms=duration_ms,
            )
            
            return response
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            log_id = self.logger.log_interaction(
                task_description="LLM generation",
                user_input=prompt,
                ai_output=f"Exception: {str(e)}",
                result="failure",
                task_type=self.task_type,
                duration_ms=duration_ms,
            )
            
            # Trigger reflection on failure
            log = self.logger.get_log(log_id)
            self.engine.reflect_on_task(log)
            
            raise


def get_reflection_summary() -> dict:
    """Get a quick summary of reflection system status.
    
    Returns:
        Dictionary with summary statistics
    """
    from .experience_db import ExperienceDB
    from .reporter import ReflectionReporter
    
    logger = ReflectionLogger()
    db = ExperienceDB()
    reporter = ReflectionReporter()
    
    log_stats = logger.get_stats()
    lesson_stats = db.get_stats()
    
    # Get recent report
    try:
        recent_report = reporter.generate_daily_report()
        recent_success_rate = recent_report.improvement_trends.get(
            "current_period_success_rate", 0
        )
    except:
        recent_success_rate = 0
    
    return {
        "total_interactions": log_stats["total_interactions"],
        "total_lessons": lesson_stats["total_lessons"],
        "active_lessons": lesson_stats["active_lessons"],
        "recent_success_rate": recent_success_rate,
        "average_lesson_success_rate": lesson_stats["average_success_rate"],
    }
