"""
MechForge AI 自我反思系统演示

这个示例展示了如何使用反思系统来记录交互、分析错误、
提取经验并生成改进报告。
"""

from mechforge_core.reflection import (
    ReflectionEngine,
    ReflectionLogger,
    ReflectionReporter,
    ExperienceDB,
)
from mechforge_core.reflection.integration import (
    with_reflection,
    ReflectionMixin,
    get_reflection_summary,
)


def demo_basic_logging():
    """演示基本的交互日志记录。"""
    print("=" * 60)
    print("演示1: 基本日志记录")
    print("=" * 60)
    
    logger = ReflectionLogger()
    
    # 记录一个成功的交互
    log_id1 = logger.log_interaction(
        task_description="回答Python问题",
        user_input="如何在Python中读取文件？",
        ai_output="使用open()函数...",
        result="success",
        task_type="qa",
    )
    print(f"✓ 记录成功交互: {log_id1}")
    
    # 记录一个失败的交互
    log_id2 = logger.log_interaction(
        task_description="代码审查",
        user_input="检查这段代码是否有bug",
        ai_output="代码看起来没问题",
        result="failure",
        task_type="code_review",
        user_feedback="漏掉了一个空指针异常",
    )
    print(f"✓ 记录失败交互: {log_id2}")
    
    # 查看统计
    stats = logger.get_stats()
    print(f"\n当前统计:")
    print(f"  总交互数: {stats['total_interactions']}")
    print(f"  成功: {stats['by_result']['success']}")
    print(f"  失败: {stats['by_result']['failure']}")
    
    return log_id1, log_id2


def demo_reflection(log_id):
    """演示反思分析。"""
    print("\n" + "=" * 60)
    print("演示2: 反思分析")
    print("=" * 60)
    
    logger = ReflectionLogger()
    engine = ReflectionEngine()
    
    # 获取日志
    log = logger.get_log(log_id)
    if log is None:
        print(f"✗ 日志未找到: {log_id}")
        return
    
    print(f"任务: {log.task_description}")
    print(f"结果: {log.result.value}")
    print(f"反馈: {log.user_feedback}")
    
    # 生成反思
    reflection = engine.reflect_on_task(log)
    
    print(f"\n反思分析:")
    print(f"  成功评估: {reflection.success_assessment}")
    print(f"  错误类型: {[e.value for e in reflection.error_types]}")
    print(f"  根本原因: {reflection.root_cause}")
    print(f"  改进策略: {reflection.improvement_strategy}")
    print(f"  成功经验: {reflection.positive_patterns}")
    
    return reflection


def demo_lessons():
    """演示经验库管理。"""
    print("\n" + "=" * 60)
    print("演示3: 经验库管理")
    print("=" * 60)
    
    db = ExperienceDB()
    
    # 搜索相关经验
    print("\n搜索 'Python' 相关经验:")
    lessons = db.search("Python code", limit=5)
    for i, lesson in enumerate(lessons, 1):
        print(f"  {i}. [{lesson.category}] {lesson.lesson_text[:60]}...")
    
    # 查看统计
    stats = db.get_stats()
    print(f"\n经验库统计:")
    print(f"  总经验数: {stats['total_lessons']}")
    print(f"  活跃经验: {stats['active_lessons']}")
    print(f"  总应用次数: {stats['total_applications']}")
    print(f"  平均成功率: {stats['average_success_rate']:.1%}")


def demo_report():
    """演示报告生成。"""
    print("\n" + "=" * 60)
    print("演示4: 报告生成")
    print("=" * 60)
    
    reporter = ReflectionReporter()
    
    # 生成日报
    report = reporter.generate_daily_report()
    
    print(reporter.format_report(report))


def demo_decorator():
    """演示装饰器用法。"""
    print("\n" + "=" * 60)
    print("演示5: 装饰器自动记录")
    print("=" * 60)
    
    @with_reflection(task_type="calculation", auto_reflect=True)
    def calculate_sum(a, b):
        """计算两个数的和。"""
        return a + b
    
    @with_reflection(task_type="calculation", auto_reflect=True)
    def calculate_divide(a, b):
        """计算两个数的商。"""
        return a / b  # 可能引发除零错误
    
    # 成功调用
    result = calculate_sum(10, 20)
    print(f"✓ calculate_sum(10, 20) = {result}")
    
    # 失败调用（会触发反思）
    try:
        result = calculate_divide(10, 0)
    except ZeroDivisionError:
        print("✗ calculate_divide(10, 0) 引发除零错误")
        print("  （已自动记录并触发反思）")


def demo_mixin():
    """演示Mixin用法。"""
    print("\n" + "=" * 60)
    print("演示6: Mixin集成")
    print("=" * 60)
    
    class CodeAssistant(ReflectionMixin):
        """代码助手，集成反思功能。"""
        
        def review_code(self, code):
            """审查代码。"""
            with self.reflect_task(
                task_description="代码审查",
                user_input=code,
                task_type="code_review",
            ) as ctx:
                # 模拟代码审查
                result = f"审查完成: 发现 {code.count('bug')} 个潜在问题"
                ctx.set_output(result)
                return result
        
        def generate_code(self, requirement):
            """生成代码。"""
            with self.reflect_task(
                task_description="代码生成",
                user_input=requirement,
                task_type="code_generation",
            ) as ctx:
                # 模拟代码生成
                result = f"# 生成的代码\n# 需求: {requirement}\nprint('Hello')"
                ctx.set_output(result)
                return result
    
    assistant = CodeAssistant()
    
    result = assistant.review_code("def foo(): pass  # bug here")
    print(f"✓ 代码审查: {result}")
    
    result = assistant.generate_code("创建一个问候函数")
    print(f"✓ 代码生成完成")


def demo_summary():
    """演示系统摘要。"""
    print("\n" + "=" * 60)
    print("演示7: 系统摘要")
    print("=" * 60)
    
    summary = get_reflection_summary()
    
    print("反思系统状态:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main():
    """运行所有演示。"""
    print("\n" + "=" * 60)
    print("MechForge AI 自我反思系统演示")
    print("=" * 60)
    
    # 运行演示
    log_id1, log_id2 = demo_basic_logging()
    demo_reflection(log_id2)
    demo_lessons()
    demo_report()
    demo_decorator()
    demo_mixin()
    demo_summary()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n提示: 使用以下命令查看更多功能:")
    print("  python -m mechforge_core.reflection --help")
    print("  python -m mechforge_core.reflection review --limit 20")
    print("  python -m mechforge_core.reflection stats")
    print("  python -m mechforge_core.reflection report --period weekly")


if __name__ == "__main__":
    main()
