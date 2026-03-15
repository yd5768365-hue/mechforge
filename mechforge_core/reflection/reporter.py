"""Report generation for reflection analytics."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .experience_db import ExperienceDB
from .logger import ReflectionLogger
from .models import ErrorType, ReflectionReport


class ReflectionReporter:
    """Reporter for generating reflection analytics and reports.
    
    This class generates periodic reports summarizing reflections,
    improvements, and recommendations for system-level optimization.
    
    Example:
        >>> reporter = ReflectionReporter()
        >>> report = reporter.generate_weekly_report()
        >>> reporter.save_report(report)
        >>> print(reporter.format_report(report))
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        logger: Optional[ReflectionLogger] = None,
        experience_db: Optional[ExperienceDB] = None,
    ):
        """Initialize the reporter.
        
        Args:
            storage_path: Base path for reflection data
            logger: Optional logger instance
            experience_db: Optional experience database instance
        """
        if storage_path is None:
            storage_path = "~/.mechforge/reflections"
            
        self.storage_path = Path(storage_path).expanduser()
        self.reports_path = self.storage_path / "reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logger or ReflectionLogger(storage_path)
        self.experience_db = experience_db or ExperienceDB(storage_path)
        
    def generate_report(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> ReflectionReport:
        """Generate a reflection report for a specific period.
        
        Args:
            period_start: Start of reporting period
            period_end: End of reporting period
            
        Returns:
            ReflectionReport with analytics
        """
        # Get interactions in period
        interactions = self._get_interactions_in_period(period_start, period_end)
        
        # Get reflections in period
        reflections = self._get_reflections_in_period(period_start, period_end)
        
        # Get new lessons in period
        lessons = self._get_lessons_in_period(period_start, period_end)
        
        # Calculate error distribution
        error_distribution = self._calculate_error_distribution(reflections)
        
        # Get top lessons
        top_lessons = self.experience_db.get_all_lessons(active_only=True, limit=5)
        
        # Calculate improvement trends
        trends = self._calculate_improvement_trends(period_start, period_end)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            interactions,
            reflections,
            error_distribution,
        )
        
        return ReflectionReport(
            period_start=period_start,
            period_end=period_end,
            total_interactions=len(interactions),
            total_reflections=len(reflections),
            new_lessons=len(lessons),
            error_type_distribution=error_distribution,
            top_lessons=top_lessons,
            improvement_trends=trends,
            recommendations=recommendations,
        )
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> ReflectionReport:
        """Generate a daily report.
        
        Args:
            date: Date for report (defaults to today)
            
        Returns:
            Daily ReflectionReport
        """
        if date is None:
            date = datetime.utcnow()
            
        period_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start + timedelta(days=1)
        
        return self.generate_report(period_start, period_end)
    
    def generate_weekly_report(self, date: Optional[datetime] = None) -> ReflectionReport:
        """Generate a weekly report.
        
        Args:
            date: Date within the week for report (defaults to today)
            
        Returns:
            Weekly ReflectionReport
        """
        if date is None:
            date = datetime.utcnow()
            
        # Find start of week (Monday)
        days_since_monday = date.weekday()
        period_start = (date - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        period_end = period_start + timedelta(days=7)
        
        return self.generate_report(period_start, period_end)
    
    def generate_monthly_report(self, date: Optional[datetime] = None) -> ReflectionReport:
        """Generate a monthly report.
        
        Args:
            date: Date within the month for report (defaults to today)
            
        Returns:
            Monthly ReflectionReport
        """
        if date is None:
            date = datetime.utcnow()
            
        period_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate end of month
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)
            
        return self.generate_report(period_start, period_end)
    
    def _get_interactions_in_period(
        self,
        start: datetime,
        end: datetime,
    ) -> List[Dict[str, Any]]:
        """Get interactions within a time period."""
        interactions = []
        
        interactions_path = self.storage_path / "interactions"
        if not interactions_path.exists():
            return interactions
            
        # Iterate through date directories
        for date_dir in interactions_path.iterdir():
            if not date_dir.is_dir():
                continue
                
            for file_path in date_dir.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    timestamp = datetime.fromisoformat(data.get("timestamp", ""))
                    
                    if start <= timestamp < end:
                        interactions.append(data)
                        
        return interactions
    
    def _get_reflections_in_period(
        self,
        start: datetime,
        end: datetime,
    ) -> List[Dict[str, Any]]:
        """Get reflections within a time period."""
        reflections = []
        
        reflections_path = self.storage_path / "reflections"
        if not reflections_path.exists():
            return reflections
            
        for date_dir in reflections_path.iterdir():
            if not date_dir.is_dir():
                continue
                
            for file_path in date_dir.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    timestamp = datetime.fromisoformat(data.get("timestamp", ""))
                    
                    if start <= timestamp < end:
                        reflections.append(data)
                        
        return reflections
    
    def _get_lessons_in_period(
        self,
        start: datetime,
        end: datetime,
    ) -> List[Dict[str, Any]]:
        """Get lessons created within a time period."""
        lessons = []
        
        lessons_path = self.storage_path / "lessons"
        if not lessons_path.exists():
            return lessons
            
        for file_path in lessons_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                created_at = datetime.fromisoformat(data.get("created_at", ""))
                
                if start <= created_at < end:
                    lessons.append(data)
                    
        return lessons
    
    def _calculate_error_distribution(
        self,
        reflections: List[Dict[str, Any]],
    ) -> Dict[ErrorType, int]:
        """Calculate distribution of error types."""
        distribution = {error_type: 0 for error_type in ErrorType}
        
        for reflection in reflections:
            error_types = reflection.get("error_types", [])
            for error_type in error_types:
                try:
                    et = ErrorType(error_type)
                    distribution[et] += 1
                except ValueError:
                    pass
                    
        return distribution
    
    def _calculate_improvement_trends(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> Dict[str, Any]:
        """Calculate improvement trends over time."""
        # Get previous period for comparison
        period_duration = period_end - period_start
        prev_start = period_start - period_duration
        prev_end = period_start
        
        prev_interactions = self._get_interactions_in_period(prev_start, prev_end)
        curr_interactions = self._get_interactions_in_period(period_start, period_end)
        
        # Calculate success rates
        prev_success = sum(
            1 for i in prev_interactions 
            if i.get("result") == "success"
        )
        curr_success = sum(
            1 for i in curr_interactions 
            if i.get("result") == "success"
        )
        
        prev_rate = prev_success / len(prev_interactions) if prev_interactions else 0
        curr_rate = curr_success / len(curr_interactions) if curr_interactions else 0
        
        return {
            "previous_period_success_rate": round(prev_rate, 3),
            "current_period_success_rate": round(curr_rate, 3),
            "improvement": round(curr_rate - prev_rate, 3),
            "total_interactions_change": len(curr_interactions) - len(prev_interactions),
        }
    
    def _generate_recommendations(
        self,
        interactions: List[Dict[str, Any]],
        reflections: List[Dict[str, Any]],
        error_distribution: Dict[ErrorType, int],
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Analyze error types
        sorted_errors = sorted(
            error_distribution.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        
        for error_type, count in sorted_errors:
            if count == 0:
                continue
                
            if error_type == ErrorType.UNDERSTANDING and count > 2:
                recommendations.append(
                    "频繁出现理解错误：建议在回答前进行需求澄清，"
                    "可以通过提问确认理解是否正确。"
                )
            elif error_type == ErrorType.KNOWLEDGE_GAP and count > 2:
                recommendations.append(
                    "知识缺失问题较多：建议增强知识库检索，"
                    "或在不确定时主动说明知识边界。"
                )
            elif error_type == ErrorType.LOGIC_ERROR and count > 2:
                recommendations.append(
                    "逻辑错误需要关注：建议采用更严谨的推理过程，"
                    "必要时展示推理步骤以便验证。"
                )
                
        # Check reflection coverage
        if interactions and len(reflections) < len(interactions) * 0.3:
            recommendations.append(
                "反思覆盖率较低：建议增加自动反思触发，"
                "特别是在任务失败时进行深度分析。"
            )
            
        # Check for repeated similar tasks
        task_types = {}
        for interaction in interactions:
            task_type = interaction.get("task_type", "general")
            task_types[task_type] = task_types.get(task_type, 0) + 1
            
        for task_type, count in task_types.items():
            if count > 5:
                recommendations.append(
                    f"'{task_type}'类型任务频繁出现：建议为此类任务"
                    f"建立专门的最佳实践指南。"
                )
                
        if not recommendations:
            recommendations.append(
                "整体表现良好：继续保持当前的反思和改进流程。"
            )
            
        return recommendations
    
    def save_report(self, report: ReflectionReport) -> Path:
        """Save a report to disk.
        
        Args:
            report: The report to save
            
        Returns:
            Path to saved report file
        """
        period_str = report.period_start.strftime("%Y-%m-%d")
        file_path = self.reports_path / f"report_{period_str}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)
            
        return file_path
    
    def format_report(self, report: ReflectionReport) -> str:
        """Format a report as a readable string.
        
        Args:
            report: The report to format
            
        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "AI 自我反思与提升报告",
            "=" * 60,
            "",
            f"报告周期: {report.period_start.strftime('%Y-%m-%d %H:%M')} "
            f"至 {report.period_end.strftime('%Y-%m-%d %H:%M')}",
            "",
            "【概览】",
            f"  总交互数: {report.total_interactions}",
            f"  反思次数: {report.total_reflections}",
            f"  新增经验: {report.new_lessons}",
            "",
            "【错误类型分布】",
        ]
        
        for error_type, count in report.error_type_distribution.items():
            if count > 0:
                lines.append(f"  {error_type.value}: {count}")
                
        lines.extend([
            "",
            "【改进趋势】",
        ])
        
        for key, value in report.improvement_trends.items():
            lines.append(f"  {key}: {value}")
            
        lines.extend([
            "",
            "【核心经验】",
        ])
        
        for i, lesson in enumerate(report.top_lessons, 1):
            lines.append(f"  {i}. [{lesson.category}] {lesson.lesson_text[:60]}...")
            
        lines.extend([
            "",
            "【改进建议】",
        ])
        
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"  {i}. {rec}")
            
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def print_report(self, report: ReflectionReport) -> None:
        """Print a formatted report to console.
        
        Args:
            report: The report to print
        """
        print(self.format_report(report))
