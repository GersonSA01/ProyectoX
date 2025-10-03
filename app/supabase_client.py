from typing import Optional
import os

from supabase import Client, create_client
from dotenv import load_dotenv


_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Return a singleton Supabase client configured from environment variables.

    Required env vars:
      - SUPABASE_URL
      - SUPABASE_ANON_KEY or SUPABASE_SERVICE_KEY (prefer service key on backend)
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    # Load .env from project root if available
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Missing SUPABASE_URL and/or SUPABASE_SERVICE_KEY/ANON_KEY in environment."
        )

    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client


