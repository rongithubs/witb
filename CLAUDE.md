# Claude Code Guidelines - Python/FastAPI

## Implementation Best Practices

### 0 — Purpose  

These rules ensure maintainability, safety, and developer velocity for Python/FastAPI applications.
**MUST** rules are enforced by CI; **SHOULD** rules are strongly recommended.

---

### 1 — Before Coding

- **BP-1 (MUST)** Ask the user clarifying questions.
- **BP-2 (SHOULD)** Draft and confirm an approach for complex work.  
- **BP-3 (SHOULD)** If ≥ 2 approaches exist, list clear pros and cons.

---

### 2 — While Coding

- **C-1 (MUST)** Follow TDD: scaffold stub -> write failing test -> implement.
- **C-2 (MUST)** Name functions with existing domain vocabulary for consistency.  
- **C-3 (SHOULD NOT)** Introduce classes when small testable functions suffice.  
- **C-4 (SHOULD)** Prefer simple, composable, testable functions.
- **C-5 (MUST)** Use proper type hints with branded types for IDs:
  ```python
  from typing import NewType
  PlayerId = NewType('PlayerId', str)     # ✅ Good
  player_id: str                          # ❌ Bad
  ```  
- **C-6 (MUST)** Use `from typing import TYPE_CHECKING` for type-only imports.
- **C-7 (SHOULD NOT)** Add comments except for critical caveats; rely on self‑explanatory code.
- **C-8 (SHOULD)** Use dataclasses or Pydantic models for structured data.
- **C-9 (SHOULD NOT)** Extract a new function unless it will be reused elsewhere, is the only way to unit-test otherwise untestable logic, or drastically improves readability of an opaque block.
- **C-10 (MUST)** Use async/await consistently throughout the application.
- **C-11 (MUST)** Follow Python naming conventions (snake_case for functions/variables, PascalCase for classes).

---

### 3 — Testing

- **T-1 (MUST)** For a simple function, colocate unit tests in `test_*.py` files in same directory as source file.
- **T-2 (MUST)** For any API change, add/extend integration tests in `tests/integration/`.
- **T-3 (MUST)** ALWAYS separate pure-logic unit tests from DB-touching integration tests.
- **T-4 (SHOULD)** Prefer integration tests over heavy mocking.  
- **T-5 (SHOULD)** Unit-test complex algorithms thoroughly.
- **T-6 (MUST)** Use pytest with async support for testing FastAPI endpoints.
- **T-7 (MUST)** Use TestClient for FastAPI endpoint testing.
- **T-8 (SHOULD)** Use pytest fixtures for database setup/teardown.
- **T-9 (SHOULD)** Test the entire structure in one assertion if possible:
  ```python
  assert result == expected_list  # Good
  
  assert len(result) == 1         # Bad
  assert result[0] == value       # Bad
  ```

---

### 4 — Database

- **D-1 (MUST)** Type DB helpers as `AsyncSession` for consistency across the application.
- **D-2 (SHOULD)** Use Pydantic models for request/response validation and SQLAlchemy models for database operations.
- **D-3 (MUST)** Use proper UUID types for all ID fields with branded types.
- **D-4 (SHOULD)** Use repository pattern to separate database operations from business logic.
- **D-5 (MUST)** Use dependency injection for database sessions: `db: AsyncSession = Depends(get_db)`.
- **D-6 (SHOULD)** Handle database transactions properly with rollback on errors.
- **D-7 (MUST)** Use SQLAlchemy relationships appropriately with proper lazy loading.

---

### 5 — Code Organization

- **O-1 (MUST)** Place code in `shared/` only if used by ≥ 2 modules.
- **O-2 (MUST)** Separate concerns: models, schemas, routes, services, repositories.
- **O-3 (SHOULD)** Use dependency injection for services and repositories.
- **O-4 (MUST)** Keep route handlers thin - delegate business logic to service functions.

---

### 6 — Tooling Gates

- **G-1 (MUST)** `black --check` passes (Python formatting).
- **G-2 (MUST)** `ruff check` or `flake8` linting passes.
- **G-3 (MUST)** `mypy` type checking passes.
- **G-4 (SHOULD)** `pytest` test suite passes.
- **G-5 (SHOULD)** Test coverage ≥ 80% for business logic.

---

### 7 - Git

- **GH-1 (MUST)** Use Conventional Commits format: https://www.conventionalcommits.org/en/v1.0.0
- **GH-2 (SHOULD NOT)** Refer to Claude or Anthropic in commit messages.

---

### 8 — FastAPI Specific

- **FA-1 (MUST)** Use proper HTTP status codes and FastAPI HTTPException.
- **FA-2 (MUST)** Use Pydantic v2 response models for all endpoints.
- **FA-3 (SHOULD)** Use FastAPI dependency injection for services, auth, etc.
- **FA-4 (MUST)** Handle errors gracefully with proper error responses.
- **FA-5 (SHOULD)** Use FastAPI background tasks for long-running operations.
- **FA-6 (MUST)** Validate request bodies with Pydantic models.
- **FA-7 (SHOULD)** Use FastAPI's automatic OpenAPI documentation.

---

## Writing Functions Best Practices

When evaluating whether a function you implemented is good or not, use this checklist:

1. Can you read the function and HONESTLY easily follow what it's doing? If yes, then stop here.
2. Does the function have very high cyclomatic complexity? If it does, then it's probably sketchy.
3. Are there any common data structures and algorithms that would make this function much easier to follow and more robust?
4. Are there any unused parameters in the function?
5. Are there any unnecessary type casts that can be moved to function arguments?
6. Is the function easily testable without mocking core features (e.g. database queries)? If not, can this function be tested as part of an integration test?
7. Does it have any hidden untested dependencies or any values that can be factored out into the arguments instead?
8. Brainstorm 3 better function names and see if the current name is the best, consistent with rest of codebase.
9. Does the function follow async/await patterns consistently?
10. Are proper type hints used for all parameters and return values?

IMPORTANT: you SHOULD NOT refactor out a separate function unless there is a compelling need, such as:
  - the refactored function is used in more than one place
  - the refactored function is easily unit testable while the original function is not AND you can't test it any other way
  - the original function is extremely hard to follow and you resort to putting comments everywhere just to explain it

## Writing Tests Best Practices

When evaluating whether a test you've implemented is good or not, use this checklist:

1. SHOULD parameterize inputs; never embed unexplained literals such as 42 or "foo" directly in the test.
2. SHOULD NOT add a test unless it can fail for a real defect.
3. SHOULD ensure the test description states exactly what the final assert verifies.
4. SHOULD compare results to independent, pre-computed expectations, never to the function's output re-used as the oracle.
5. SHOULD follow the same lint, type-safety, and style rules as prod code.
6. SHOULD express invariants or axioms whenever practical. Use `hypothesis` library for property-based testing:
```python
from hypothesis import given, strategies as st
import pytest

@given(st.text(), st.text())
def test_concatenation_length_property(a: str, b: str):
    result = concatenate_strings(a, b)
    assert len(result) == len(a) + len(b)
```

7. Unit tests for a function should be grouped under `class TestFunctionName:`.
8. Use pytest fixtures for setup/teardown and dependency injection.
9. ALWAYS use strong assertions over weaker ones e.g. `assert x == 1` instead of `assert x >= 1`.
10. SHOULD test edge cases, realistic input, unexpected input, and value boundaries.
11. SHOULD NOT test conditions that are caught by the type checker.
12. Use `pytest.mark.asyncio` for testing async functions.
13. Use FastAPI TestClient for testing endpoints.

## Code Organization

- `witb-backend/` - FastAPI backend server
  - `witb-backend/routes/` - API route handlers
  - `witb-backend/services/` - Business logic
  - `witb-backend/repositories/` - Database operations
  - `witb-backend/models/` - SQLAlchemy models
  - `witb-backend/schemas/` - Pydantic models
  - `witb-backend/tests/` - Test files
- `witb-frontend/` - Next.js frontend
- `scraper/` - Web scraping utilities
- `shared/` - Shared utilities and types

## Remember Shortcuts

### QNEW
When I type "qnew", this means:
```
Understand all BEST PRACTICES listed in CLAUDE.md.
Your code SHOULD ALWAYS follow these best practices.
```

### QPLAN
When I type "qplan", this means:
```
Analyze similar parts of the codebase and determine whether your plan:
- is consistent with rest of codebase
- introduces minimal changes
- reuses existing code
- follows Python/FastAPI best practices
```

### QCODE
When I type "qcode", this means:
```
Implement your plan and make sure your new tests pass.
Always run tests to make sure you didn't break anything else.
Always run `black` on the newly created files to ensure standard formatting.
Always run `ruff check` and `mypy` to make sure linting and type checking passes.
```

### QCHECK
When I type "qcheck", this means:
```
You are a SKEPTICAL senior Python engineer.
Perform this analysis for every MAJOR code change you introduced (skip minor changes):

1. CLAUDE.md checklist Writing Functions Best Practices.
2. CLAUDE.md checklist Writing Tests Best Practices.
3. CLAUDE.md checklist Implementation Best Practices.
```

### QCHECKF
When I type "qcheckf", this means:
```
You are a SKEPTICAL senior Python engineer.
Perform this analysis for every MAJOR function you added or edited (skip minor changes):

1. CLAUDE.md checklist Writing Functions Best Practices.
```

### QCHECKT
When I type "qcheckt", this means:
```
You are a SKEPTICAL senior Python engineer.
Perform this analysis for every MAJOR test you added or edited (skip minor changes):

1. CLAUDE.md checklist Writing Tests Best Practices.
```

### QUX
When I type "qux", this means:
```
Imagine you are a human UX tester of the feature you implemented. 
Output a comprehensive list of scenarios you would test, sorted by highest priority.
```

### QGIT
When I type "qgit", this means:
```
Add all changes to staging, create a commit, and push to remote.

Follow this checklist for writing your commit message:
- SHOULD use Conventional Commits format: https://www.conventionalcommits.org/en/v1.0.0
- SHOULD NOT refer to Claude or Anthropic in the commit message.
- SHOULD structure commit message as follows:
<type>[optional scope]: <description>
[optional body]
[optional footer(s)]
```

## Development Commands

- **Start backend**: `cd witb-backend && uvicorn main:app --reload`
- **Run tests**: `cd witb-backend && pytest`
- **Format code**: `cd witb-backend && black .`
- **Lint code**: `cd witb-backend && ruff check .`
- **Type check**: `cd witb-backend && mypy .`
- **Start frontend**: `cd witb-frontend && npm run dev`