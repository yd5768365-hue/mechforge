---
name: verify
description: Run tests and verify application starts before marking task complete
proactive: true
triggers:
  - after implementing new features
  - after fixing bugs
  - before claiming task completion
---

# Steps
1. Run project tests if available (pytest, npm test, etc.)
2. Try to start/import the application
3. Check for any import errors or runtime issues
4. Only report complete if all checks pass