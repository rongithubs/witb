# OPT-CONTEXTLOG.md
# WITB Database Project Memory Document

## 🏗️ Architecture Foundation

### Project Overview
**WITB (What's In The Bag)** is a professional golf equipment tracking application that aggregates and displays professional golfers' equipment data, world rankings, and tournament information. The system combines web scraping, API integration, and a modern web application to provide comprehensive golf equipment insights.

### Technology Stack

**Backend (FastAPI + Python 3.11+)**
- `witb-backend/main.py` - FastAPI application entry point
- `fastapi` + `uvicorn[standard]` - Web framework and ASGI server
- `sqlalchemy>=2.0` + `asyncpg` - Async ORM and PostgreSQL driver
- `aiosqlite` - SQLite support for local development
- `pydantic>=2.0` - Data validation and serialization
- `supabase>=2.10.0` - Authentication and cloud database
- `httpx` + `beautifulsoup4` + `scrapingbee` - Web scraping
- `google-generativeai` - AI-powered data extraction
- `python-jose[cryptography]` - JWT authentication

**Frontend (Next.js 15 + React 19)**
- `witb-frontend/app/` - Next.js App Router structure
- `next@15.3.4` + `react@19.0.0` - Framework and UI library
- `@supabase/supabase-js@2.55.0` - Authentication integration
- `tailwindcss@4` - Styling framework
- `@radix-ui/*` - Accessible UI components
- `swr@2.3.3` - Data fetching and caching
- `lucide-react` - Icon system

**Data Sources & Scraping**
- `scraper/` - Standalone scraping modules
- PGA Tour official rankings and equipment data
- LPGA Tour player information  
- Official World Golf Ranking (OGWR)
- ESPN Golf API for tournament data
- eBay API for equipment pricing

### Key Entry Points

**Backend**
- `witb-backend/main.py:app` - FastAPI application instance
- `witb-backend/database.py` - Database connection and session management
- `witb-backend/models.py` - SQLAlchemy ORM models

**Frontend**  
- `witb-frontend/app/layout.tsx` - Root layout with providers
- `witb-frontend/app/page.tsx` - Main application page
- `witb-frontend/lib/api.ts` - API client with authentication

**Scraping**
- `scraper/witb_scraper.py` - Core WITB data scraper
- `scraper/tournament_scraper.py` - Tournament winner scraper
- `scraper/witb_update_main.py` - Main scraping orchestrator

### Directory Structure

```
witb/
├── witb-backend/           # FastAPI backend
│   ├── main.py            # App entry point
│   ├── models.py          # SQLAlchemy models
│   ├── database.py        # DB configuration
│   ├── schemas.py         # Pydantic models
│   ├── dependencies.py    # FastAPI dependencies
│   ├── routes/            # API route handlers
│   │   ├── players.py     # Player CRUD operations
│   │   ├── witb.py        # Equipment data endpoints
│   │   ├── tournaments.py # Tournament information
│   │   └── ebay.py        # Pricing integration
│   ├── services/          # Business logic layer
│   │   ├── player_service.py
│   │   ├── witb_service.py
│   │   └── tournament_service.py
│   ├── repositories/      # Data access layer
│   ├── auth/              # Authentication logic
│   └── tests/             # Test suites
├── witb-frontend/         # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   │   ├── ui/           # Base UI components
│   │   ├── PlayerTable.tsx
│   │   └── ClubLeaderboard.tsx
│   ├── providers/         # React context providers
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility functions
│   └── types/             # TypeScript definitions
└── scraper/               # Data collection modules
    ├── witb_scraper.py    # Equipment scraper
    ├── tournament_scraper.py # Tournament data
    └── database_updater.py   # DB sync utilities
```

### Data Flow Patterns

**Data Collection Flow:**
1. `scraper/` modules fetch raw data from sources
2. Data is processed and validated using Pydantic models
3. `services/` layer applies business logic and transformations
4. `repositories/` layer handles database persistence
5. `routes/` expose data via RESTful API endpoints

**Frontend Data Flow:**
1. React components use `hooks/usePlayersData.ts` for data fetching
2. SWR manages caching, revalidation, and error handling
3. `lib/api.ts` handles authenticated requests to backend
4. Supabase manages user authentication and sessions
5. Context providers manage global state (auth, favorites, theme)

## 🛠️ Development Patterns

### Code Organization Standards

**Backend Architecture (Repository Pattern)**
- `routes/` - Thin route handlers, delegate to services (CLAUDE.md O-4)
- `services/` - Business logic, orchestrate repositories
- `repositories/` - Database operations, return domain objects
- `schemas/` - Pydantic models for API contracts
- `models/` - SQLAlchemy ORM models

**Frontend Architecture (Custom Hooks Pattern)**
- `hooks/` - Data fetching and state management logic
- `providers/` - Global state via React Context
- `components/` - Presentational components with clear props
- `lib/` - Utility functions and API clients

### Adding New Features

**Backend Feature Development:**
1. **Define Data Models** - Add SQLAlchemy model in `models.py`
2. **Create Pydantic Schemas** - Add request/response models in `schemas.py`
3. **Build Repository** - Database operations in `repositories/`
4. **Implement Service** - Business logic in `services/`
5. **Add Route Handler** - Thin controller in `routes/`
6. **Write Tests** - Unit tests in `tests/unit/`, integration in `tests/integration/`

**Frontend Feature Development:**
1. **Create Custom Hook** - Data fetching logic in `hooks/`
2. **Build Components** - UI components with TypeScript props
3. **Add Routes** - New pages in `app/` directory
4. **Update Types** - TypeScript definitions in `types/`
5. **Add Tests** - Component tests using Vitest + Testing Library

### Testing Strategy

**Backend Testing (pytest + asyncio)**
- **Unit Tests** - `tests/unit/` - Test individual functions/services
- **Integration Tests** - `tests/integration/` - Test API endpoints with database
- **Fixtures** - `tests/fixtures/` - Mock data and API responses
- Test database isolation using transactions
- AsyncMock for mocking async dependencies

**Key Testing Patterns:**
```python
# Unit test example - tests/unit/test_player_service.py
class TestPlayerService:
    @pytest.fixture
    def player_service(self, mock_db):
        service = PlayerService(mock_db)
        service.player_repo = AsyncMock()
        return service
    
    def test_enrich_witb_items_with_urls_adds_brand_urls(self, player_service):
        # Test implementation following CLAUDE.md T-6
```

**Frontend Testing (Vitest + Testing Library)**
- Component tests for user interactions
- Hook tests for data fetching logic
- Integration tests for full user workflows

### Database Patterns

**Model Relationships:**
```python
# models.py - Key relationships
class Player(Base):
    witb_items = relationship("WITBItem", back_populates="player", lazy="selectin")

class User(Base):
    favorite_players = relationship("FavoritePlayer", back_populates="user", lazy="selectin")
```

**Repository Pattern:**
```python
# repositories/player_repository.py
class PlayerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_players_paginated(self, page: int, per_page: int, tour: str | None):
        # Database query implementation
```

**Service Layer:**
```python
# services/player_service.py
class PlayerService:
    def __init__(self, db: AsyncSession):
        self.player_repo = PlayerRepository(db)
        self.witb_repo = WITBRepository(db)
    
    async def create_player(self, player: schemas.PlayerCreate):
        # Business logic implementation
```

## 🔧 Operational Knowledge

### Environment Setup

**Backend Setup:**
```bash
cd witb-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

**Frontend Setup:**
```bash
cd witb-frontend
npm install
npm run dev
```

**Environment Variables:**
- Backend: `DATABASE_URL`, `LOCAL_DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Scraper: `SCRAPINGBEE_API_KEY`, `GEMINI_API_KEY`

### Database Configuration

**Development Database:**
- SQLite: `sqlite+aiosqlite:///./dev.db`
- PostgreSQL: `postgresql+asyncpg://user:pass@localhost/db`

**Production Database:**
- Supabase PostgreSQL with connection pooling
- Automatic table creation on startup via `main.py:lifespan`

### External API Integrations

**Supabase Authentication:**
- JWT-based authentication using `@supabase/supabase-js`
- User management with email/phone signup
- Row-level security for user data

**ScrapingBee API:**
- Handles JavaScript-heavy websites
- Rate limiting and proxy rotation
- Used for PGA Tour data collection

**eBay API:**
- Equipment pricing data
- Product search and filtering
- Integrated in tournament winner displays

**ESPN Golf API:**
- Tournament information and leaderboards
- Player statistics and rankings
- Real-time scoring data

### Build and Deployment

**Backend Commands:**
```bash
# Development
uvicorn main:app --reload

# Testing
pytest                    # Run all tests
pytest tests/unit/       # Unit tests only
pytest tests/integration/ # Integration tests only

# Code Quality
black .                  # Format code
ruff check .            # Lint code
mypy .                  # Type checking
```

**Frontend Commands:**
```bash
npm run dev             # Development server
npm run build          # Production build
npm run start           # Production server
npm run lint           # ESLint
npm run test           # Vitest tests
```

### Data Scraping Operations

**Manual Scraping:**
```bash
cd scraper
python witb_update_main.py      # Update all WITB data
python tournament_scraper.py    # Update tournament winners
python populate_lpga_data.py    # LPGA player data
```

**Automated Updates:**
- Tournament data: Cached for 30 minutes
- Player rankings: Updated via scraping services
- Equipment data: Incremental updates to avoid duplicates

## 🎯 Domain Knowledge

### Business Logic Rules

**Player Data Management:**
- Players are identified by UUID with unique constraints
- Multiple tours supported: "OGWR", "PGA Tour", "LPGA Tour"
- Rankings are tour-specific and time-based
- Photo URLs are optional but preferred for UI

**Equipment Data (WITB Items):**
- Categories: "Driver", "Fairway", "Iron", "Wedge", "Putter", etc.
- Brand and model are required fields
- Loft and shaft specifications are optional
- Product URLs are enriched with brand-specific links
- Source URLs track data provenance

**User Features:**
- Authentication via Supabase (email/phone)
- Favorite players with unique constraints per user
- Personalized equipment recommendations based on favorites

**Tournament Integration:**
- Winners are cached to reduce API calls
- Equipment data is linked to tournament winners
- eBay pricing integration for winner's equipment
- Historical tournament data preservation

### User Workflows

**Main Application Flow:**
1. **Landing Page** - Display top OGWR players by default
2. **Player Search** - Real-time search across player names
3. **Equipment Details** - Click player to view full equipment bag
4. **Favorite Management** - Authenticated users can save favorite players
5. **Tournament Banner** - Latest winner with equipment and pricing
6. **Club Leaderboard** - Popular equipment across all players

**Authentication Flow:**
1. **Sign Up/Sign In** - Supabase Auth UI integration
2. **Session Management** - Automatic token refresh
3. **Protected Features** - Favorites require authentication
4. **Profile Management** - User data via `/auth/me` endpoint

**Admin/Scraping Workflows:**
1. **Data Collection** - Scheduled scraping of source websites
2. **Data Validation** - Pydantic models ensure data quality
3. **Duplicate Prevention** - Database constraints prevent data duplication
4. **Error Handling** - Graceful fallbacks when external APIs fail

### Data Models and Relationships

**Core Entities:**
```
Player (1) ←→ (N) WITBItem     # Player's equipment
User (1) ←→ (N) FavoritePlayer # User's saved players
Player (1) ←→ (N) FavoritePlayer # Popular players
```

**Key Constraints:**
- `players.name` + `players.tour` should be unique per tour
- `user_favorite_players.user_id` + `player_id` must be unique
- UUIDs used for all primary keys with branded types

**Data Enrichment:**
- Brand URLs are automatically added based on brand names
- Equipment categories are standardized during ingestion
- Missing player photos are handled gracefully in UI

## 🤖 AI Assistant Guidance

### Common Development Tasks

**Adding a New API Endpoint:**
1. **Model First** - Define SQLAlchemy model in `models.py`
2. **Schema Definition** - Create Pydantic request/response models in `schemas.py`
3. **Repository Layer** - Add database operations in `repositories/`
4. **Service Logic** - Implement business logic in `services/`
5. **Route Handler** - Create thin controller in `routes/`
6. **Testing** - Add unit and integration tests
7. **Frontend Hook** - Create custom hook for data fetching

**Adding a New React Component:**
1. **Define Props Interface** - TypeScript interface for component props
2. **Implement Component** - Use existing UI patterns and Radix components
3. **Add to Storybook** - Document component usage (if applicable)
4. **Write Tests** - Component and interaction tests
5. **Update Parent Components** - Integrate into existing layouts

**Database Schema Changes:**
1. **Update Model** - Modify SQLAlchemy models in `models.py`
2. **Create Migration** - Generate Alembic migration (if using migrations)
3. **Update Schemas** - Modify Pydantic models for API contracts
4. **Update Services** - Adjust business logic for new fields
5. **Test Data Migration** - Ensure existing data migrates correctly

### Debugging Approaches

**Backend Issues:**
- **Database Errors** - Check `database.py` connection configuration
- **API Errors** - Use FastAPI automatic docs at `/docs` endpoint
- **Service Errors** - Check service layer business logic and repository calls
- **Authentication Issues** - Verify Supabase configuration and JWT handling

**Frontend Issues:**
- **Data Fetching** - Check SWR cache and API responses in browser DevTools
- **Authentication** - Verify Supabase client configuration and session state
- **Component Errors** - Use React Error Boundaries and console logging
- **Type Errors** - Ensure TypeScript types match API contracts

**Scraping Issues:**
- **Rate Limiting** - Check ScrapingBee quota and implement delays
- **Data Quality** - Validate scraped data against Pydantic schemas
- **Website Changes** - Update selectors when source sites change structure
- **API Failures** - Implement fallback data sources

### Performance Considerations

**Backend Optimization:**
- Use `lazy="selectin"` for SQLAlchemy relationships to avoid N+1 queries
- Implement pagination for large datasets (25 items per page)
- Cache expensive operations (tournament data cached 30 minutes)
- Use async/await consistently throughout the application

**Frontend Optimization:**
- SWR provides automatic caching and revalidation
- React.memo() used for expensive components
- Lazy loading for large datasets
- Optimistic updates for user interactions

**Database Optimization:**
- UUID primary keys with proper indexing
- Foreign key constraints for data integrity
- Connection pooling for high concurrency
- Read replicas for read-heavy operations (future consideration)

### Quality Standards

**Code Quality Requirements:**
- **Backend** - Must pass `black --check`, `ruff check`, `mypy`
- **Frontend** - Must pass `npm run lint`, TypeScript compilation
- **Testing** - Minimum 80% coverage for business logic
- **Documentation** - All public APIs must have docstrings

**CLAUDE.md Compliance:**
- Follow TDD: stub → test → implement
- Thin route handlers, fat services
- Use branded types for IDs (`PlayerId = NewType('PlayerId', str)`)
- Prefer integration tests over heavy mocking
- Use Conventional Commits for git messages

**Security Requirements:**
- Never log or expose API keys or secrets
- Validate all user inputs with Pydantic
- Use parameterized queries for database operations
- Implement proper CORS configuration
- Sanitize all scraped data before storage

### Common Pitfalls to Avoid

1. **Database Sessions** - Always use `AsyncSession = Depends(get_db)` dependency injection
2. **Error Handling** - Use FastAPI HTTPException with proper status codes
3. **Type Safety** - Use branded types for all ID fields to prevent confusion
4. **Testing** - Don't mock core functionality; prefer integration tests
5. **API Design** - Keep route handlers thin; move logic to services
6. **Authentication** - Always verify JWT tokens on protected endpoints
7. **Data Scraping** - Implement rate limiting and respect robots.txt
8. **Performance** - Use database relationships efficiently to avoid N+1 queries

### Development Workflow

**Feature Development Checklist:**
- [ ] Create or update data models
- [ ] Define API contracts with Pydantic schemas
- [ ] Implement repository layer for data access
- [ ] Add business logic in service layer
- [ ] Create thin route handlers
- [ ] Write comprehensive tests (unit + integration)
- [ ] Update frontend hooks and components
- [ ] Add TypeScript types for new data structures
- [ ] Test authentication integration if applicable
- [ ] Update documentation and examples

**Code Review Guidelines:**
- Verify CLAUDE.md compliance
- Check test coverage and quality
- Ensure proper error handling
- Validate security considerations
- Confirm performance implications
- Review database query efficiency
- Verify TypeScript type safety