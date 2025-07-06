# WITB Backend

A FastAPI backend for the What's In The Bag golf equipment tracking application, refactored following Python/FastAPI best practices.

## Architecture

The backend follows a clean architecture pattern with separation of concerns:

```
witb-backend/
├── main.py                 # FastAPI app entry point
├── routes/                 # API route handlers (thin layer)
│   ├── players.py         
│   └── tournaments.py     
├── services/               # Business logic layer
│   ├── player_service.py  
│   └── tournament_service.py
├── repositories/           # Data access layer
│   ├── player_repository.py
│   └── witb_repository.py
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic request/response models
├── database.py            # Database configuration
├── dependencies.py        # FastAPI dependencies
├── exceptions.py          # Custom exception classes
├── custom_types.py        # Branded types for type safety
├── brand_urls.py          # Brand URL utilities
└── tests/                 # Test suite
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── conftest.py        # Pytest configuration
```

## Key Features

- **Clean Architecture**: Separation of routes, services, and repositories
- **Type Safety**: Branded types for IDs and comprehensive type hints
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Code Quality**: Black formatting, Ruff linting, MyPy type checking
- **Async/Await**: Consistent async patterns throughout

## Development

### Setup
```bash
cd witb-backend
pip install -r requirements-dev.txt
```

### Commands
```bash
# Format code
make format

# Run linting
make lint

# Type checking
make typecheck

# Run tests
make test

# Run all checks
make check-all

# Start server
make run
```

### Testing
- **Unit tests**: `tests/unit/` - Test business logic in isolation
- **Integration tests**: `tests/integration/` - Test API endpoints end-to-end
- **Run tests**: `pytest` or `make test`

## API Endpoints

### Players
- `POST /players/` - Create player
- `GET /players` - Get paginated players
- `GET /players/search` - Search player by name
- `GET /players/{id}` - Get player by ID
- `POST /players/{id}/witb_items/` - Add WITB item

### Tournaments
- `GET /tournament-winner` - Get latest tournament winner
- `GET /tournament-winner/debug` - Debug tournament scraping

## Code Quality Standards

This project follows the guidelines in `CLAUDE.md`:

- **MUST**: Black formatting, Ruff linting, MyPy type checking
- **MUST**: Comprehensive test coverage for business logic
- **MUST**: Proper error handling with custom exceptions
- **SHOULD**: Repository pattern for database operations
- **SHOULD**: Dependency injection for services

## Database

Uses SQLAlchemy with async support:
- **Development**: SQLite (dev.db)
- **Production**: PostgreSQL (Supabase)

## Refactoring Benefits

1. **Maintainability**: Clear separation of concerns
2. **Testability**: Business logic isolated in services
3. **Type Safety**: Branded types prevent ID mixups
4. **Error Handling**: Consistent exception patterns
5. **Code Quality**: Automated formatting and linting