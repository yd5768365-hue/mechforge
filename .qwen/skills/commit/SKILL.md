---
name: commit
description: Stage all changes, create a descriptive commit message, and push
proactive: true
triggers:
  - after completing code changes
  - when user mentions "commit" or "提交"
  - when work is ready to be saved
---

# Steps
1. Run `git status` to see changes
2. Review diff and create meaningful commit message
3. Stage and commit with `git add . && git commit -m "message"`
4. Push to remote