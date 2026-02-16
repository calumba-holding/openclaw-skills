# Phase 7: Testing & Polish Specification

**Phase:** 7 of 8  
**Title:** Testing & Polish  
**Objective:** Comprehensive testing, error handling, and polish  
**Status:** Draft  
**Dependencies:** Phase 1-6

---

## 1. Overview

### Purpose

This phase ensures reliability through **comprehensive testing** and **error handling**.

### Test Categories

| Category | Count | Focus |
|----------|-------|-------|
| Unit | 50+ | Individual functions |
| Integration | 20+ | Hook + OpenClaw |
| End-to-end | 10+ | Full workflows |
| Edge cases | 30+ | Error handling |

### Target Coverage

- **Unit tests**: 90%+ coverage
- **Integration**: All components
- **Errors**: All error paths

---

## 2. Test Structure

### Directory Structure

```
tokenQrusher/
├── tests/
│   ├── unit/
│   │   ├── test_classifier.py
│   │   ├── test_context.py
│   │   └── test_model.py
│   ├── integration/
│   │   ├── test_hooks.py
│   │   └── test_cli.py
│   ├── e2e/
│   │   └── test_optimization.py
│   └── edge/
│       └── test_errors.py
├── pytest.ini
└── conftest.py
```

---

## 3. Test Implementation

### 3.1 Unit Tests

```python
# tests/unit/test_classifier.py
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from context_optimizer import classify_prompt
from model_router import classify_task

class TestContextClassifier:
    def test_simple_greeting(self):
        result = classify_prompt("hi")
        assert result["complexity"] == "simple"
    
    def test_standard_work(self):
        result = classify_prompt("write a function")
        assert result["complexity"] in ["medium", "complex"]
    
    def test_complex_design(self):
        result = classify_prompt("design a system architecture")
        assert result["complexity"] == "complex"

class TestModelClassifier:
    def test_background_task(self):
        result = classify_task("check email")
        assert result["tier"] == "quick"
    
    def test_simple_read(self):
        result = classify_task("read the file")
        assert result["tier"] == "quick"
```

### 3.2 Integration Tests

```python
# tests/integration/test_hooks.py
import pytest
import json
from pathlib import Path

class TestContextHook:
    def test_hook_loads(self):
        """Test that context hook loads"""
        # Would test actual hook loading
        pass
    
    def test_filtering(self):
        """Test that filtering works"""
        pass

class TestCLI:
    def test_context_command(self):
        """Test context CLI command"""
        import subprocess
        result = subprocess.run(
            ["python3", "bin/tokenqrusher", "context", "hi"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
    
    def test_budget_command(self):
        """Test budget CLI command"""
        pass
```

### 3.3 Edge Case Tests

```python
# tests/edge/test_errors.py
import pytest

class TestErrorHandling:
    def test_missing_config(self):
        """Test handling of missing config"""
        pass
    
    def test_corrupt_json(self):
        """Test handling of corrupt JSON"""
        pass
    
    def test_network_failure(self):
        """Test handling of network failures"""
        pass
    
    def test_invalid_prompt(self):
        """Test handling of invalid prompts"""
        pass
```

---

## 4. Error Handling Requirements

### By Component

| Component | Error Handling |
|-----------|----------------|
| Hooks | Graceful degradation, log errors |
| CLI | User-friendly messages, exit codes |
| Scripts | Try/except, fallback values |
| Config | Validation, defaults |

### Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Config error |
| 4 | Network error |
| 5 | OpenClaw not found |

---

## 5. Polish Items

### CLI Polish

- [ ] Colored output
- [ ] Progress indicators
- [ ] Better help text
- [ ] Auto-completion

### Documentation Polish

- [ ] Fix all TODO comments
- [ ] Complete all docstrings
- [ ] Add code examples
- [ ] Fix typos

### Code Polish

- [ ] Remove dead code
- [ ] Simplify complex functions
- [ ] Add type hints
- [ ] Standardize formatting

---

## 6. Test Execution

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific category
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### CI/CD

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov
```

---

## 7. Acceptance Criteria

### Test Requirements

- [ ] 50+ unit tests passing
- [ ] 20+ integration tests passing
- [ ] 10+ e2e tests passing
- [ ] 30+ edge case tests passing
- [ ] 90%+ code coverage

### Polish Requirements

- [ ] All error paths handled
- [ ] CLI help complete
- [ ] Documentation complete
- [ ] No TODO comments

---

## 8. References

- pytest documentation
- Python testing best practices

---

*This specification defines Phase 7 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
