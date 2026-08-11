# Claude Code Guidelines - Python/FastAPI

## Orientation

WITB ("What's In The Bag") tracks the equipment professional golfers carry. It
scrapes tour and equipment sources, stores players and their bag items, and
serves them to a Next.js frontend.

**Request path:** `routes/` → `services/` → `repositories/` → `models.py`.
Routers wired in `main.py`: `auth`, `ebay`, `players`, `tournaments`,
`user_bag`, `witb`.

**Data:** `database.py` reads `DATABASE_URL` (Supabase Postgres via asyncpg) and
falls back to `LOCAL_DATABASE_URL` (SQLite). It builds a single module-level
`engine`; request code should reach the DB through `Depends(get_db)`, not that
engine.

**Auth:** Supabase issues the JWT; the backend verifies it locally in
`auth/service.py` using `python-jose`. Protected routes depend on
`auth.dependencies.get_current_user_from_db`.

**Background work:** `main.py` starts an `AsyncIOScheduler` in the app lifespan
for the weekly OGWR ranking refresh.

### What you cannot infer by reading the code

- **Tests must never touch the production database.** `conftest.py` swaps the app
  lifespan for a no-op, because the real one runs `create_all` against
  `DATABASE_URL` and shares one asyncpg connection across per-test event loops
  ("another operation is in progress"). Do not remove that override.
- **`patch("auth.dependencies.get_current_user_from_db")` silently does nothing.**
  FastAPI resolves dependencies at route-definition time, so the patch never
  takes effect. Use `app.dependency_overrides[...]` instead. Several existing
  tests still get this wrong and fail because of it.
- **`services/tournament_scraper_service.py` bypasses the layering** — it imports
  `engine` directly and runs raw SQL rather than accepting an `AsyncSession`.
  Tests that patch `engine.begin` fail for this reason; it is a known wart, not a
  pattern to copy.
- **A few `node_modules/` files are committed at the repo root** (`react`, `swr`,
  `dequal`, `use-sync-external-store`, `.package-lock.json`). They were added
  before `.gitignore` covered them, and git keeps tracking already-committed
  files. They are not the real dependency tree — the frontend's lives in
  `witb-frontend/node_modules/`. Ignore them; don't sync or edit them.
- **The suite is not green.** As of 2026-08 it runs 24–25 failed / 167–168 passed
  / 2 skipped in ~11s. Those failures are tracked work, not necessarily damage
  from your change — run `pytest` before and after and compare the two counts.
- **One test is genuinely flaky**, which is why the count above is a range:
  `test_favorite_player_repository.py::test_get_user_favorites_returns_ordered_list`
  inserts rows that share a `CURRENT_TIMESTAMP` and then asserts an order the DB
  never promised. It fails roughly 1 run in 3. A one-test change in the failure
  count is probably this, not you.

### Frontend orientation

Next.js 15 App Router + React 19 in `witb-frontend/`. Pages: `/` (players),
`/changes` (weekly bag-change feed), `/my-bag`, `/profile`.

- `lib/api.ts` and `lib/fetcher.ts` reach the backend at `NEXT_PUBLIC_API_URL`
  (default `http://localhost:8000`) — so the backend must be running separately.
- Server state lives in SWR hooks under `hooks/` (`usePlayersData`, `useUserBag`,
  `useWITBChanges`, …), not in component state. Add a hook rather than fetching
  inside a component.
- Cross-cutting state is in `providers/` (`auth-provider`, `favorites-provider`,
  `theme-provider`), wired in `app/layout.tsx`.
- `lib/supabase.ts` holds the browser Supabase client; it issues the JWT the
  backend verifies.
- Tests are Vitest, colocated in `__tests__/` next to what they cover. Run with
  `npm test` from `witb-frontend/`. Unlike the backend suite, this one is green
  (103/103 when last run, 2026-08).

Two traps when running the frontend:

- **A fresh git worktree has no frontend deps.** `witb-frontend/node_modules` is
  gitignored, so `npm test` there dies with `vitest: command not found` until you
  run `npm install`. Don't reach for `npx vitest` instead — it silently installs a
  *different* major version into an npx cache and fails on unrelated errors.
- **`npm test` alone watches and never exits.** Use `npm test -- --run` for a
  single pass; a bare `npm test` will hang a scripted session.

### Reference docs

`contextlog.md` and `OPT-CONTEXTLOG.md` are historical architecture notes last
updated 2025-09. They predate the `user_bag`, `bag_change`, and `witb_sync`
subsystems. Where they disagree with the code, the code wins.

## Implementation Best Practices

### 0 — Purpose  

These rules ensure maintainability, safety, and developer velocity for Python/FastAPI applications.
**MUST** rules are strongly enforced by review; **SHOULD** rules are strongly recommended.
(There is no CI pipeline yet — see the tooling gates in §6 and run them locally.)

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

- **O-1 (MUST)** Keep helpers next to their only caller; promote to a shared module
  only once ≥ 2 modules use them. (There is no `shared/` package today — don't
  create one for a single consumer.)
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
  - `witb-backend/auth/` - Supabase JWT verification and auth routes
  - `witb-backend/models.py` - SQLAlchemy models
  - `witb-backend/schemas.py` - Pydantic models
  - `witb-backend/custom_types.py` - Branded ID types
  - `witb-backend/tests/` - Test files (`unit/`, `integration/`, `fixtures/`)
- `witb-frontend/` - Next.js frontend
- `scraper/` - Web scraping utilities

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