# AI自我反思与提升技能 (Self-Reflection Skill)

## 概述

这是MechForge AI的**内部开发辅助技能**，帮助AI在开发过程中从交互中学习、记录经验、持续优化代码质量。

**注意**：此技能为AI开发辅助工具，不对外暴露CLI命令。

## 核心功能

### 1. 交互日志记录 (ReflectionLogger)
- 记录开发过程中的关键交互
- 支持任务结果标记（成功/部分成功/失败）
- 按日期自动组织存储

### 2. 反思分析引擎 (ReflectionEngine)
- 自动分析任务成功/失败原因
- 识别错误类型（理解错误、知识缺失、逻辑错误等）
- 生成改进策略和成功经验
- 从反思中提取可复用的经验

### 3. 经验库管理 (ExperienceDB)
- 存储和管理提取的经验教训
- 支持关键词搜索和相关性检索
- 跟踪经验应用次数和成功率

### 4. 报告生成 (ReflectionReporter)
- 生成开发周期报告
- 分析错误类型分布和改进趋势
- 提供开发优化建议

### 5. 集成工具 (Integration)
- 装饰器自动记录函数调用
- Mixin类为现有类添加反思能力
- LLM包装器自动增强提示词

## 使用方式

### 基础用法

```python
from mechforge_core.reflection import ReflectionLogger, ReflectionEngine

# 创建日志记录器
logger = ReflectionLogger()

# 记录交互
log_id = logger.log_interaction(
    task_description="实现用户认证",
    user_input="添加JWT验证",
    ai_output=generated_code,
    result="partial",  # success/partial/failure
    task_type="coding",
    user_feedback="缺少回滚脚本",
)

# 创建反思引擎
engine = ReflectionEngine()

# 获取日志并生成反思
log = logger.get_log(log_id)
reflection = engine.reflect_on_task(log)

print(f"改进策略: {reflection.improvement_strategy}")
```

### 使用装饰器自动记录

```python
from mechforge_core.reflection.integration import with_reflection

@with_reflection(task_type="refactoring", auto_reflect=True)
def refactor_code(code):
    # 重构代码
    return refactored_code

# 调用时会自动记录，失败时自动反思
refactor_code(source_code)
```

### 使用Mixin集成到类

```python
from mechforge_core.reflection.integration import ReflectionMixin

class CodeGenerator(ReflectionMixin):
    def generate(self, requirement):
        with self.reflect_task("code_generation", requirement) as ctx:
            result = self.do_generation(requirement)
            ctx.set_output(result)
            return result
```

### 检索相关经验

```python
from mechforge_core.reflection import ExperienceDB, ReflectionEngine

engine = ReflectionEngine()

# 在执行任务前检索相关经验
lessons = engine.retrieve_lessons("数据库迁移", limit=3)

for lesson in lessons:
    print(f"[{lesson.category}] {lesson.lesson_text}")
```

### 生成报告

```python
from mechforge_core.reflection import ReflectionReporter

reporter = ReflectionReporter()

# 生成周报
report = reporter.generate_weekly_report()
print(reporter.format_report(report))
```

## 数据存储

反思数据存储在：`~/.mechforge/reflections/`

```
~/.mechforge/reflections/
├── interactions/     # 原始交互日志
├── reflections/      # 反思分析结果
├── lessons/          # 提取的经验教训
└── reports/          # 生成的报告
```

## 配置

```python
from mechforge_core.reflection import ReflectionConfig

config = ReflectionConfig(
    storage_path="~/.mechforge/reflections",
    auto_reflect=True,                    # 失败时自动反思
    auto_reflect_threshold="partial",     # 触发自动反思的阈值
    retention_days=90,                    # 数据保留天数
    enable_rag_integration=True,          # 启用RAG集成
    max_lessons_per_query=3,              # 每次查询最大经验数
    min_lesson_confidence=0.6,            # 最小经验置信度
)
```

## 错误类型

- `understanding`: 理解错误（误解需求）
- `knowledge_gap`: 知识缺失
- `logic_error`: 逻辑错误
- `format_style`: 格式/样式问题
- `context_limit`: 上下文限制
- `execution`: 执行错误
- `other`: 其他

## 最佳实践

1. **记录有意义的交互**：专注于非平凡的编码任务
2. **失败时反思**：当结果不是"success"时进行反思
3. **主动应用经验**：在执行相似任务前检查相关经验
4. **保持轻量**：不要对简单、常规任务过度反思
5. **隐私优先**：反思中不包含用户敏感数据

## 完整示例

```python
from mechforge_core.reflection import (
    ReflectionLogger, 
    ReflectionEngine,
    ReflectionReporter,
)

# 1. 执行任务前 - 检索相关经验
engine = ReflectionEngine()
lessons = engine.retrieve_lessons("API接口设计")
if lessons:
    print(f"发现 {len(lessons)} 条相关经验")

# 2. 执行任务并记录
logger = ReflectionLogger()
log_id = logger.log_interaction(
    task_description="设计REST API",
    user_input="创建用户管理接口",
    ai_output=api_design_code,
    result="partial",
    user_feedback="缺少错误处理",
    task_type="api_design",
)

# 3. 反思经验
log = logger.get_log(log_id)
reflection = engine.reflect_on_task(log)

print(f"根本原因: {reflection.root_cause}")
print(f"改进策略: {reflection.improvement_strategy}")

# 4. 定期生成报告
reporter = ReflectionReporter()
report = reporter.generate_weekly_report()
reporter.print_report(report)
```

## 与MechForge模块集成

- **AI对话模式**: 记录对话历史，学习用户编码偏好
- **知识库模式**: 记录检索失败案例，改进检索策略
- **CAE工作台**: 记录仿真失败和解决方案

## 隐私与安全

- 所有数据本地存储，不上传云端
- 支持敏感信息自动脱敏
- 可配置数据保留策略
- 用户反馈可选择性记录
