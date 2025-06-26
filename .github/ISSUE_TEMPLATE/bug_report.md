@"
---
name: 🐞 Bug report
about: Report a bug or unexpected behavior
title: "[BUG] "
labels: bug
assignees: ''
---

### 🐛 Describe the bug
A clear and concise description of what the bug is.

### 🧪 Steps to reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Run '...'
3. See error

### 📷 Screenshots (if any)

### 🖥️ Environment (please complete the following):
- OS: [e.g. Windows, Linux]
- Python version
- Repo branch/version

### 📎 Additional context
Add any other context about the problem here.
"@ | Out-File -Encoding utf8 .github\ISSUE_TEMPLATE\bug_report.md
