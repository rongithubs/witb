# WITB Supabase Auth Integration

## Overview

This implementation provides user authentication using Supabase Auth with FastAPI, following a hybrid approach where:
- **Supabase handles**: User authentication, JWT tokens, social logins, magic links
- **Local database handles**: Player data, WITB items, business logic

## Setup Instructions

### 1. Environment Variables

Add these to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### 2. Supabase Project Setup

1. Create a new Supabase project at https://supabase.com
2. Go to **Settings > API** to get your keys
3. Configure authentication providers in **Authentication > Providers**:
   - Google OAuth
   - Apple Sign-In
   - Magic Links (email/SMS)

### 3. Database Migration

Run the application once to create the new User tables:

```bash
uvicorn main:app --reload
```

This will automatically create:
- `users` table
- Proper relationships with existing data

## API Endpoints

### Authentication Endpoints

- `GET /auth/health` - Auth system health check
- `GET /auth/me` - Get current user info (requires JWT token)
- `POST /auth/verify-token` - Verify JWT token validity

### Protected Endpoints

To protect any endpoint, use the auth dependencies:

```python
from auth.dependencies import get_current_user_from_db

@router.get("/protected")
async def protected_endpoint(
    current_user: schemas.User = Depends(get_current_user_from_db)
):
    return {"message": f"Hello {current_user.email}!"}
```

## Frontend Integration

### 1. Install Supabase Client

```bash
npm install @supabase/supabase-js
```

### 2. Initialize Supabase

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

### 3. Authentication Examples

#### Magic Link Signup/Login
```typescript
const { error } = await supabase.auth.signInWithOtp({
  email: 'user@example.com'
})
```

#### SMS Magic Link
```typescript
const { error } = await supabase.auth.signInWithOtp({
  phone: '+1234567890'
})
```

#### Google OAuth
```typescript
const { error } = await supabase.auth.signInWithOAuth({
  provider: 'google'
})
```

#### Get JWT Token for API Calls
```typescript
const { data: { session } } = await supabase.auth.getSession()
const token = session?.access_token

// Use token in API calls
const response = await fetch('/api/protected', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

## Architecture Benefits

1. **Fast Development**: No custom auth implementation needed
2. **High Conversion**: SMS + social login options increase signup rates
3. **Secure**: Industry-standard JWT tokens and OAuth flows
4. **Scalable**: Supabase handles auth infrastructure
5. **Future-Ready**: Easy to add passkeys, MFA, etc.

## Next Steps

1. Configure social login providers in Supabase dashboard
2. Implement frontend auth flows
3. Add user-specific features (favorites, preferences)
4. Consider migrating to Supabase database later if needed

## Development Commands

```bash
# Start backend with auth
uvicorn main:app --reload

# Run auth tests
pytest tests/unit/test_auth_service.py -v
pytest tests/integration/test_auth_routes.py -v

# Type checking
mypy auth/

# Formatting
black auth/
```