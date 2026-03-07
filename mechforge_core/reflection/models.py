"""Data models for the reflection system."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Types of errors that can occur."""
    UNDERSTANDING = "understanding"  # Misinterpreted requirements
    KNOWLEDGE_GAP = "knowledge_gap"  # Missing information
    LOGIC_ERROR = "logic_error"  # Incorrect reasoning
    FORMAT_STYLE = "format_style"  # Presentation problems
    CONTEXT_LIMIT = "context_limit"  # Insufficient context
    EXECUTION = "execution"  # Runtime/execution error
    OTHER = "other"


class TaskResult(str, Enum):
    """Possible task outcomes."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class InteractionLog(BaseModel):
    """Record of a single interaction or task execution.
    
    Attributes:
        id: Unique identifier for this log entry
        timestamp: When the interaction occurred
        session_id: Identifier for the session/context
        task_type: Category of task (e.g., "coding", "analysis", "qa")
        task_description: Brief description of what was attempted
        user_input: The input/prompt received
        ai_output: The response/output generated
        result: Success status of the task
        user_feedback: Optional feedback from user (positive/negative/correction)
        metadata: Additional context (model used, parameters, etc.)
        duration_ms: Time taken to complete the task
    """
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    task_type: str = "general"
    task_description: str
    user_input: str
    ai_output: str
    result: TaskResult = TaskResult.UNKNOWN
    user_feedback: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class ReflectionEntry(BaseModel):
    """A structured reflection on a past interaction.
    
    Attributes:
        id: Unique identifier for this reflection
        log_id: Reference to the original interaction log
        timestamp: When the reflection was created
        success_assessment: Evaluation of task success
        error_types: Categories of errors identified
        root_cause: Analysis of why errors occurred
        improvement_strategy: Specific actions to prevent recurrence
        positive_patterns: What worked well
        lessons_extracted: List of lesson IDs derived from this reflection
        confidence: Confidence in the reflection analysis (0-1)
    """
    id: UUID = Field(default_factory=uuid4)
    log_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success_assessment: str
    error_types: List[ErrorType] = Field(default_factory=list)
    root_cause: str
    improvement_strategy: str
    positive_patterns: str
    lessons_extracted: List[UUID] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class Lesson(BaseModel):
    """An extracted lesson that can be applied to future tasks.
    
    Attributes:
        id: Unique identifier for this lesson
        created_at: When the lesson was extracted
        updated_at: When the lesson was last modified
        source_reflections: IDs of reflections that contributed to this lesson
        category: Lesson category (error_prevention, best_practice, etc.)
        context_pattern: Pattern to match for relevance
        trigger_keywords: Keywords that indicate this lesson may be relevant
        lesson_text: The actual lesson content
        application_count: How many times this lesson has been applied
        success_rate: Success rate when applying this lesson
        priority: Priority for retrieval (1-10)
        active: Whether this lesson is currently active
    """
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source_reflections: List[UUID] = Field(default_factory=list)
    category: str = "general"
    context_pattern: str
    trigger_keywords: List[str] = Field(default_factory=list)
    lesson_text: str
    application_count: int = 0
    success_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    priority: int = Field(ge=1, le=10, default=5)
    active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class ReflectionReport(BaseModel):
    """A periodic report summarizing reflections and improvements.
    
    Attributes:
        period_start: Start of reporting period
        period_end: End of reporting period
        total_interactions: Number of interactions in period
        total_reflections: Number of reflections created
        new_lessons: Number of new lessons extracted
        error_type_distribution: Count of each error type
        top_lessons: Most frequently applied lessons
        improvement_trends: Metrics showing improvement over time
        recommendations: System-level improvement suggestions
    """
    period_start: datetime
    period_end: datetime
    total_interactions: int
    total_reflections: int
    new_lessons: int
    error_type_distribution: Dict[ErrorType, int]
    top_lessons: List[Lesson]
    improvement_trends: Dict[str, Any]
    recommendations: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ReflectionConfig(BaseModel):
    """Configuration for the reflection system.
    
    Attributes:
        storage_path: Where to store reflection data
        auto_reflect: Whether to automatically reflect on failures
        auto_reflect_threshold: Result level that triggers auto-reflection
        retention_days: How long to keep interaction logs
        enable_rag_integration: Whether to integrate with RAG system
        reflection_prompt_template: Template for generating reflections
    """
    storage_path: str = "~/.mechforge/reflections"
    auto_reflect: bool = True
    auto_reflect_threshold: TaskResult = TaskResult.PARTIAL
    retention_days: int = 90
    enable_rag_integration: bool = True
    reflection_prompt_template: Optional[str] = None
    max_lessons_per_query: int = 3
    min_lesson_confidence: float = 0.6
