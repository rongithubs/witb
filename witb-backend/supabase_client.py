"""Supabase client configuration following CLAUDE.md patterns."""

import os
from typing import Optional

from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()


class SupabaseConfig:
    """Configuration for Supabase client."""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

        if not self.url or not self.anon_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
            )

        if not self.jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET must be set for JWT verification")


# Global Supabase client instances
_supabase_config: Optional[SupabaseConfig] = None
_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def get_supabase_config() -> SupabaseConfig:
    """Get Supabase configuration."""
    global _supabase_config
    if _supabase_config is None:
        _supabase_config = SupabaseConfig()
    return _supabase_config


def get_supabase_client() -> Client:
    """Get Supabase client for regular operations."""
    global _supabase_client
    if _supabase_client is None:
        config = get_supabase_config()
        _supabase_client = create_client(config.url, config.anon_key)
    return _supabase_client


def get_supabase_admin_client() -> Client:
    """Get Supabase admin client for privileged operations."""
    global _supabase_admin_client
    if _supabase_admin_client is None:
        config = get_supabase_config()
        if not config.service_role_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY must be set for admin operations"
            )
        _supabase_admin_client = create_client(config.url, config.service_role_key)
    return _supabase_admin_client
