"""Experience database for storing and retrieving learned lessons."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from .models import Lesson


class ExperienceDB:
    """Database for managing learned lessons and experiences.
    
    This class provides storage, retrieval, and management of lessons
    extracted from reflections. It supports vector-based similarity search
    for finding relevant lessons.
    
    Example:
        >>> db = ExperienceDB()
        >>> db.store_lesson(lesson)
        >>> lessons = db.search("How to handle errors", limit=5)
        >>> db.update_lesson_success(lesson_id, success=True)
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the experience database.
        
        Args:
            storage_path: Base path for storing lessons. Defaults to ~/.mechforge/reflections
        """
        if storage_path is None:
            storage_path = os.path.expanduser("~/.mechforge/reflections")
        self.storage_path = Path(storage_path)
        self.lessons_path = self.storage_path / "lessons"
        self._ensure_directories()
        
    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        self.lessons_path.mkdir(parents=True, exist_ok=True)
        
    def store_lesson(self, lesson: Lesson) -> UUID:
        """Store a lesson in the database.
        
        Args:
            lesson: The lesson to store
            
        Returns:
            UUID of the stored lesson
        """
        file_path = self.lessons_path / f"{lesson.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(lesson.model_dump(), f, indent=2, ensure_ascii=False)
        return lesson.id
    
    def get_lesson(self, lesson_id: UUID) -> Optional[Lesson]:
        """Retrieve a specific lesson.
        
        Args:
            lesson_id: UUID of the lesson
            
        Returns:
            The Lesson if found, None otherwise
        """
        file_path = self.lessons_path / f"{lesson_id}.json"
        if not file_path.exists():
            return None
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Lesson(**data)
    
    def update_lesson(self, lesson: Lesson) -> bool:
        """Update an existing lesson.
        
        Args:
            lesson: The updated lesson
            
        Returns:
            True if update was successful
        """
        lesson.updated_at = datetime.utcnow()
        return self.store_lesson(lesson) is not None
    
    def delete_lesson(self, lesson_id: UUID) -> bool:
        """Delete a lesson from the database.
        
        Args:
            lesson_id: UUID of the lesson to delete
            
        Returns:
            True if deletion was successful
        """
        file_path = self.lessons_path / f"{lesson_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_priority: int = 1,
        active_only: bool = True,
    ) -> List[Lesson]:
        """Search for lessons matching a query.
        
        This is a keyword-based search. In production, this would use
        vector similarity search with embeddings.
        
        Args:
            query: Search query
            limit: Maximum number of results
            category: Optional category filter
            min_priority: Minimum priority level
            active_only: Only return active lessons
            
        Returns:
            List of matching lessons sorted by relevance
        """
        query_keywords = set(self._extract_keywords(query))
        scored_lessons = []
        
        for file_path in self.lessons_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                lesson = Lesson(**data)
                
                # Apply filters
                if active_only and not lesson.active:
                    continue
                if category and lesson.category != category:
                    continue
                if lesson.priority < min_priority:
                    continue
                    
                # Calculate relevance score
                score = self._calculate_relevance(lesson, query_keywords)
                
                if score > 0:
                    scored_lessons.append((score, lesson))
                    
        # Sort by score (descending) and return top results
        scored_lessons.sort(key=lambda x: x[0], reverse=True)
        return [lesson for _, lesson in scored_lessons[:limit]]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z_]+\b', text.lower())
        
        # Filter out common stopwords
        stopwords = {
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "and",
            "or", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall", "can",
            "need", "dare", "ought", "used", "的", "了", "在", "是", "和",
        }
        
        keywords = [w for w in set(words) if len(w) > 2 and w not in stopwords]
        return keywords
    
    def _calculate_relevance(self, lesson: Lesson, query_keywords: set) -> float:
        """Calculate relevance score between lesson and query."""
        # Combine lesson keywords from multiple fields
        lesson_text = f"{lesson.context_pattern} {lesson.lesson_text}"
        lesson_keywords = set(self._extract_keywords(lesson_text))
        lesson_keywords.update(lesson.trigger_keywords)
        
        # Calculate Jaccard similarity
        intersection = len(query_keywords & lesson_keywords)
        union = len(query_keywords | lesson_keywords)
        
        if union == 0:
            return 0.0
            
        base_score = intersection / union
        
        # Boost score based on lesson priority and success rate
        priority_boost = lesson.priority / 10.0 * 0.2
        success_boost = lesson.success_rate * 0.2
        
        return base_score + priority_boost + success_boost
    
    def update_lesson_success(
        self,
        lesson_id: UUID,
        success: bool,
    ) -> bool:
        """Update a lesson's success statistics.
        
        Args:
            lesson_id: UUID of the lesson
            success: Whether the application was successful
            
        Returns:
            True if update was successful
        """
        lesson = self.get_lesson(lesson_id)
        if lesson is None:
            return False
            
        lesson.application_count += 1
        
        # Update success rate using moving average
        if lesson.application_count == 1:
            lesson.success_rate = 1.0 if success else 0.0
        else:
            old_rate = lesson.success_rate
            n = lesson.application_count
            lesson.success_rate = (old_rate * (n - 1) + (1.0 if success else 0.0)) / n
            
        return self.update_lesson(lesson) is not None
    
    def get_lessons_by_category(self, category: str) -> List[Lesson]:
        """Get all lessons in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of lessons in the category
        """
        lessons = []
        
        for file_path in self.lessons_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("category") == category:
                    lessons.append(Lesson(**data))
                    
        return lessons
    
    def get_all_lessons(
        self,
        active_only: bool = True,
        limit: Optional[int] = None,
    ) -> List[Lesson]:
        """Get all lessons from the database.
        
        Args:
            active_only: Only return active lessons
            limit: Maximum number of lessons to return
            
        Returns:
            List of lessons
        """
        lessons = []
        
        for file_path in self.lessons_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                lesson = Lesson(**data)
                
                if active_only and not lesson.active:
                    continue
                    
                lessons.append(lesson)
                
        # Sort by priority and success rate
        lessons.sort(key=lambda l: (l.priority, l.success_rate), reverse=True)
        
        if limit:
            lessons = lessons[:limit]
            
        return lessons
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the experience database.
        
        Returns:
            Dictionary with statistics
        """
        total = 0
        active = 0
        by_category: Dict[str, int] = {}
        total_applications = 0
        avg_success_rate = 0.0
        
        for file_path in self.lessons_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                total += 1
                
                if data.get("active", True):
                    active += 1
                    
                category = data.get("category", "general")
                by_category[category] = by_category.get(category, 0) + 1
                
                total_applications += data.get("application_count", 0)
                avg_success_rate += data.get("success_rate", 0)
                
        if total > 0:
            avg_success_rate /= total
            
        return {
            "total_lessons": total,
            "active_lessons": active,
            "by_category": by_category,
            "total_applications": total_applications,
            "average_success_rate": round(avg_success_rate, 3),
        }
    
    def merge_similar_lessons(
        self,
        similarity_threshold: float = 0.8,
    ) -> int:
        """Merge lessons that are very similar to each other.
        
        Args:
            similarity_threshold: Minimum similarity to merge
            
        Returns:
            Number of lessons merged
        """
        lessons = self.get_all_lessons(active_only=False)
        merged_count = 0
        
        for i, lesson1 in enumerate(lessons):
            if not lesson1.active:
                continue
                
            for lesson2 in lessons[i + 1:]:
                if not lesson2.active:
                    continue
                    
                similarity = self._calculate_similarity(lesson1, lesson2)
                
                if similarity >= similarity_threshold:
                    # Merge lesson2 into lesson1
                    self._merge_lessons(lesson1, lesson2)
                    lesson2.active = False
                    self.update_lesson(lesson2)
                    merged_count += 1
                    
        return merged_count
    
    def _calculate_similarity(self, lesson1: Lesson, lesson2: Lesson) -> float:
        """Calculate similarity between two lessons."""
        text1 = f"{lesson1.context_pattern} {lesson1.lesson_text}"
        text2 = f"{lesson2.context_pattern} {lesson2.lesson_text}"
        
        keywords1 = set(self._extract_keywords(text1))
        keywords2 = set(self._extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
            
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def _merge_lessons(self, target: Lesson, source: Lesson) -> None:
        """Merge source lesson into target lesson."""
        # Combine source reflections
        target.source_reflections.extend(source.source_reflections)
        target.source_reflections = list(set(target.source_reflections))
        
        # Combine keywords
        target.trigger_keywords = list(set(
            target.trigger_keywords + source.trigger_keywords
        ))
        
        # Update statistics
        total_apps = target.application_count + source.application_count
        if total_apps > 0:
            target.success_rate = (
                target.success_rate * target.application_count +
                source.success_rate * source.application_count
            ) / total_apps
        target.application_count = total_apps
        
        # Use higher priority
        target.priority = max(target.priority, source.priority)
        
        self.update_lesson(target)
