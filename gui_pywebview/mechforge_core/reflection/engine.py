"""Reflection engine for analyzing interactions and generating insights."""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    ErrorType,
    InteractionLog,
    Lesson,
    ReflectionConfig,
    ReflectionEntry,
    TaskResult,
)


class ReflectionEngine:
    """Engine for analyzing interactions and generating reflections.
    
    This class provides the core reflection capabilities:
    - Analyzing interaction logs
    - Generating structured reflections
    - Extracting lessons
    - Retrieving relevant past lessons
    
    Example:
        >>> engine = ReflectionEngine()
        >>> reflection = engine.reflect_on_task(log_id)
        >>> lessons = engine.retrieve_lessons("How to optimize Python code")
    """
    
    DEFAULT_REFLECTION_TEMPLATE = """请对以下AI交互进行反思分析：

【任务描述】
{task_description}

【用户输入】
{user_input}

【AI输出】
{ai_output}

【任务结果】
{result}

【用户反馈】
{feedback}

请按以下结构进行分析：

1. 任务成功评估：
   - 任务是否成功完成？
   - 如果没有，具体失败表现是什么？

2. 错误类型分析（可多选）：
   - 理解错误：是否误解了用户需求？
   - 知识缺失：是否缺少必要信息？
   - 逻辑错误：推理过程是否有问题？
   - 格式问题：输出格式是否恰当？
   - 上下文限制：是否因上下文不足导致？

3. 根本原因：
   - 为什么会出现这些问题？
   - 错误假设是什么？

4. 改进策略：
   - 如何避免类似错误？
   - 应该采用什么方法/工具？

5. 成功经验：
   - 本次任务中哪些做法是好的？
   - 值得保留的策略是什么？

请以结构化格式输出分析结果。"""

    def __init__(self, config: Optional[ReflectionConfig] = None):
        """Initialize the reflection engine.
        
        Args:
            config: Configuration for the engine
        """
        self.config = config or ReflectionConfig()
        self.storage_path = Path(os.path.expanduser(self.config.storage_path))
        self.reflections_path = self.storage_path / "reflections"
        self._ensure_directories()
        
    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        self.reflections_path.mkdir(parents=True, exist_ok=True)
        
    def reflect_on_task(
        self,
        log: InteractionLog,
        reflection_text: Optional[str] = None,
    ) -> ReflectionEntry:
        """Generate a reflection on a task.
        
        Args:
            log: The interaction log to reflect on
            reflection_text: Optional pre-generated reflection text
            
        Returns:
            The created ReflectionEntry
        """
        # If no reflection text provided, generate one
        if reflection_text is None:
            reflection_text = self._generate_reflection_text(log)
            
        # Parse the reflection text to extract structured information
        parsed = self._parse_reflection_text(reflection_text)
        
        # Create reflection entry
        reflection = ReflectionEntry(
            log_id=log.id,
            success_assessment=parsed.get("success_assessment", ""),
            error_types=parsed.get("error_types", []),
            root_cause=parsed.get("root_cause", ""),
            improvement_strategy=parsed.get("improvement_strategy", ""),
            positive_patterns=parsed.get("positive_patterns", ""),
            confidence=parsed.get("confidence", 0.8),
        )
        
        # Save reflection
        self._save_reflection(reflection)
        
        # Extract lessons
        lessons = self._extract_lessons(log, reflection)
        reflection.lessons_extracted = [lesson.id for lesson in lessons]
        
        # Update saved reflection with lesson IDs
        self._save_reflection(reflection)
        
        return reflection
    
    def _generate_reflection_text(self, log: InteractionLog) -> str:
        """Generate reflection text using template.
        
        In a real implementation, this might call an LLM.
        For now, we use rule-based analysis.
        """
        template = (
            self.config.reflection_prompt_template 
            or self.DEFAULT_REFLECTION_TEMPLATE
        )
        
        # Simple rule-based analysis as fallback
        feedback = log.user_feedback or "无"
        
        # Analyze based on result and feedback
        if log.result == TaskResult.SUCCESS:
            success_assessment = "任务成功完成"
            error_types = []
            root_cause = "无明显错误"
            improvement = "继续保持当前做法"
            positive = "成功完成了任务目标"
        elif log.result == TaskResult.FAILURE:
            success_assessment = "任务未能成功完成"
            error_types = self._detect_error_types(log)
            root_cause = self._infer_root_cause(log)
            improvement = self._suggest_improvement(log)
            positive = "尝试了解决问题"
        else:
            success_assessment = "任务部分完成"
            error_types = self._detect_error_types(log)
            root_cause = self._infer_root_cause(log)
            improvement = self._suggest_improvement(log)
            positive = "部分解决了问题"
            
        # Format as reflection text
        reflection = f"""1. 任务成功评估：
{success_assessment}

2. 错误类型分析：
{', '.join(e.value for e in error_types) if error_types else '无明显错误'}

3. 根本原因：
{root_cause}

4. 改进策略：
{improvement}

5. 成功经验：
{positive}"""
        
        return reflection
    
    def _detect_error_types(self, log: InteractionLog) -> List[ErrorType]:
        """Detect error types from log and feedback."""
        errors = []
        feedback = (log.user_feedback or "").lower()
        output = log.ai_output.lower()
        
        # Pattern matching for error types
        if any(kw in feedback for kw in ["误解", "理解", "意思", "需求"]):
            errors.append(ErrorType.UNDERSTANDING)
        if any(kw in feedback for kw in ["不知道", "不了解", "缺少", "缺失"]):
            errors.append(ErrorType.KNOWLEDGE_GAP)
        if any(kw in feedback for kw in ["逻辑", "推理", "错误", "不对"]):
            errors.append(ErrorType.LOGIC_ERROR)
        if any(kw in feedback for kw in ["格式", "排版", "样式", "不清晰"]):
            errors.append(ErrorType.FORMAT_STYLE)
        if any(kw in feedback for kw in ["上下文", "背景", "信息不足"]):
            errors.append(ErrorType.CONTEXT_LIMIT)
            
        if not errors and log.result != TaskResult.SUCCESS:
            errors.append(ErrorType.OTHER)
            
        return errors
    
    def _infer_root_cause(self, log: InteractionLog) -> str:
        """Infer root cause from log data."""
        if log.user_feedback:
            return f"根据用户反馈: {log.user_feedback[:100]}..."
        if log.result == TaskResult.FAILURE:
            return "任务执行失败，需要更多上下文信息"
        return "未知原因"
    
    def _suggest_improvement(self, log: InteractionLog) -> str:
        """Suggest improvements based on error analysis."""
        suggestions = []
        
        if log.user_feedback:
            suggestions.append("仔细分析用户反馈并针对性改进")
        if log.result != TaskResult.SUCCESS:
            suggestions.append("在回答前进行更全面的分析")
            suggestions.append("必要时请求更多上下文信息")
            
        return "; ".join(suggestions) if suggestions else "继续保持"
    
    def _parse_reflection_text(self, text: str) -> Dict[str, Any]:
        """Parse reflection text into structured data."""
        result = {
            "success_assessment": "",
            "error_types": [],
            "root_cause": "",
            "improvement_strategy": "",
            "positive_patterns": "",
            "confidence": 0.8,
        }
        
        # Extract sections using regex
        sections = {
            "success_assessment": r"1\.\s*任务成功评估[:：]\s*(.*?)(?=2\.|$)",
            "error_types": r"2\.\s*错误类型分析[:：]\s*(.*?)(?=3\.|$)",
            "root_cause": r"3\.\s*根本原因[:：]\s*(.*?)(?=4\.|$)",
            "improvement_strategy": r"4\.\s*改进策略[:：]\s*(.*?)(?=5\.|$)",
            "positive_patterns": r"5\.\s*成功经验[:：]\s*(.*?)(?=\n\n|$)",
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                if key == "error_types":
                    result[key] = self._parse_error_types(content)
                else:
                    result[key] = content
                    
        return result
    
    def _parse_error_types(self, text: str) -> List[ErrorType]:
        """Parse error types from text."""
        error_map = {
            "理解": ErrorType.UNDERSTANDING,
            "知识": ErrorType.KNOWLEDGE_GAP,
            "逻辑": ErrorType.LOGIC_ERROR,
            "格式": ErrorType.FORMAT_STYLE,
            "上下文": ErrorType.CONTEXT_LIMIT,
            "执行": ErrorType.EXECUTION,
        }
        
        errors = []
        for keyword, error_type in error_map.items():
            if keyword in text:
                errors.append(error_type)
                
        return errors
    
    def _extract_lessons(
        self,
        log: InteractionLog,
        reflection: ReflectionEntry,
    ) -> List[Lesson]:
        """Extract lessons from a reflection."""
        lessons = []
        
        # Create lesson from improvement strategy
        if reflection.improvement_strategy:
            lesson = Lesson(
                source_reflections=[reflection.id],
                category="error_prevention",
                context_pattern=log.task_description,
                trigger_keywords=self._extract_keywords(log.task_description),
                lesson_text=reflection.improvement_strategy,
                priority=7 if reflection.error_types else 5,
            )
            lessons.append(lesson)
            
        # Create lesson from positive patterns
        if reflection.positive_patterns:
            lesson = Lesson(
                source_reflections=[reflection.id],
                category="best_practice",
                context_pattern=log.task_description,
                trigger_keywords=self._extract_keywords(log.task_description),
                lesson_text=reflection.positive_patterns,
                priority=6,
            )
            lessons.append(lesson)
            
        return lessons
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z_]+\b', text.lower())
        # Filter out common words and return unique keywords
        stopwords = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and"}
        keywords = [w for w in set(words) if len(w) > 2 and w not in stopwords]
        return keywords[:10]  # Limit to 10 keywords
    
    def _save_reflection(self, reflection: ReflectionEntry) -> None:
        """Save reflection to disk."""
        date_str = reflection.timestamp.strftime("%Y-%m-%d")
        date_dir = self.reflections_path / date_str
        date_dir.mkdir(exist_ok=True)
        
        file_path = date_dir / f"{reflection.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(reflection.model_dump(), f, indent=2, ensure_ascii=False)
    
    def retrieve_lessons(
        self,
        context: str,
        limit: int = 3,
        category: Optional[str] = None,
    ) -> List[Lesson]:
        """Retrieve relevant lessons for a given context.
        
        Args:
            context: The current task context
            limit: Maximum number of lessons to return
            category: Optional category filter
            
        Returns:
            List of relevant lessons
        """
        # This is a simplified implementation
        # In production, this would use vector similarity search
        context_keywords = set(self._extract_keywords(context))
        
        lessons = []
        lessons_path = self.storage_path / "lessons"
        
        if not lessons_path.exists():
            return lessons
            
        for file_path in lessons_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                lesson = Lesson(**data)
                
                if not lesson.active:
                    continue
                if category and lesson.category != category:
                    continue
                    
                # Calculate relevance score
                lesson_keywords = set(lesson.trigger_keywords)
                overlap = len(context_keywords & lesson_keywords)
                score = overlap / max(len(context_keywords), 1)
                
                if score > 0.1:  # Minimum relevance threshold
                    lessons.append((score, lesson))
                    
        # Sort by score and return top lessons
        lessons.sort(key=lambda x: x[0], reverse=True)
        return [lesson for _, lesson in lessons[:limit]]
    
    def enhance_prompt_with_reflections(
        self,
        prompt: str,
        context: str,
    ) -> str:
        """Enhance a prompt with relevant past lessons.
        
        Args:
            prompt: The original prompt
            context: Task context for retrieving lessons
            
        Returns:
            Enhanced prompt with reflection guidance
        """
        lessons = self.retrieve_lessons(context)
        
        if not lessons:
            return prompt
            
        reflection_context = "\n\n【过往经验参考】\n"
        for i, lesson in enumerate(lessons, 1):
            reflection_context += f"{i}. {lesson.lesson_text}\n"
            
        return prompt + reflection_context
