---
name: self-reflection
description: AI开发辅助 - 自我反思与持续改进，从编码交互中学习并优化表现
proactive: true
triggers:
  - after completing complex development tasks
  - when encountering repeated coding errors
  - when user mentions "反思" or "总结" or "review"
  - at end of development session
  - when implementation pattern emerges
---

# AI Self-Reflection Skill for Development

## Purpose

This skill helps AI assistants learn from development interactions, record coding experiences, and continuously improve code quality through structured self-reflection.

**Note**: This is an internal development aid, not a user-facing feature.

## When to Use

- After completing complex multi-step coding tasks
- When similar errors occur repeatedly
- When user provides feedback on code quality
- At the end of a development session
- When a successful pattern emerges that should be remembered

## Core Workflow

### 1. Record Interaction

During development, record key interactions:

```python
from mechforge_core.reflection import ReflectionLogger

logger = ReflectionLogger()
log_id = logger.log_interaction(
    task_description="Implement user authentication",
    user_input="Add JWT token validation",
    ai_output="<generated code>",
    result="success",  # success/partial/failure
    task_type="coding",
)
```

### 2. Reflect on Task

After task completion (especially on partial/failure), generate reflection:

```python
from mechforge_core.reflection import ReflectionEngine

engine = ReflectionEngine()
log = logger.get_log(log_id)
reflection = engine.reflect_on_task(log)

# Key insights available:
# - reflection.error_types: What went wrong
# - reflection.root_cause: Why it happened
# - reflection.improvement_strategy: How to avoid in future
# - reflection.positive_patterns: What worked well
```

### 3. Apply Learned Lessons

Before similar tasks, retrieve relevant experiences:

```python
# Get relevant lessons for current context
lessons = engine.retrieve_lessons("JWT authentication implementation")

# Enhance prompt with learned lessons
enhanced_prompt = engine.enhance_prompt_with_reflections(
    prompt=current_task,
    context=current_task
)
```

## Integration Patterns

### Using Decorator

Automatically log function calls:

```python
from mechforge_core.reflection.integration import with_reflection

@with_reflection(task_type="refactoring")
def refactor_code(code):
    # Refactoring logic
    return refactored_code
```

### Using Mixin

Add reflection to service classes:

```python
from mechforge_core.reflection.integration import ReflectionMixin

class CodeGenerator(ReflectionMixin):
    def generate(self, requirement):
        with self.reflect_task("code_generation", requirement) as ctx:
            code = self._do_generation(requirement)
            ctx.set_output(code)
            return code
```

## Error Types

- `understanding`: Misunderstood requirements
- `knowledge_gap`: Missing technical knowledge
- `logic_error`: Incorrect implementation logic
- `format_style`: Code style/formatting issues
- `context_limit`: Insufficient project context
- `execution`: Runtime/execution errors

## Data Storage

Reflection data stored locally in: `~/.mechforge/reflections/`
- `interactions/`: Raw interaction logs
- `reflections/`: Processed reflection entries
- `lessons/`: Extracted lessons for future use

## Best Practices

1. **Record meaningful interactions**: Focus on non-trivial coding tasks
2. **Reflect on failures**: Always reflect when result is not "success"
3. **Apply lessons proactively**: Check for relevant lessons before similar tasks
4. **Keep it lightweight**: Don't over-reflect on simple, routine tasks
5. **Privacy first**: No user-sensitive data in reflections

## Example: Complete Workflow

```python
from mechforge_core.reflection import ReflectionLogger, ReflectionEngine

# Step 1: Before task - check for relevant lessons
engine = ReflectionEngine()
lessons = engine.retrieve_lessons("database migration")
if lessons:
    print(f"Found {len(lessons)} relevant lessons from past experiences")

# Step 2: Execute task and record
logger = ReflectionLogger()
log_id = logger.log_interaction(
    task_description="Create database migration",
    user_input="Add users table with indexes",
    ai_output=migration_code,
    result="partial",
    user_feedback="Missing rollback script",
    task_type="database",
)

# Step 3: Reflect on the experience
log = logger.get_log(log_id)
reflection = engine.reflect_on_task(log)

# Step 4: Use insights for improvement
print(f"Root cause: {reflection.root_cause}")
print(f"Strategy: {reflection.improvement_strategy}")
```
