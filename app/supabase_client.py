from typing import Optional
import os
import time
import logging
from functools import wraps

from supabase import Client, create_client
from dotenv import load_dotenv
import httpx

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


def retry_on_network_error(max_retries: int = 3, initial_delay: float = 1.0):
    """Decorator para reintentar operaciones que fallan por errores de red."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (httpx.ReadError, httpx.ConnectError, httpx.TimeoutException, OSError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Intento {attempt + 1} falló con error de red: {e}. Reintentando en {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= 2  # Backoff exponencial
                    else:
                        logger.error(f"Todos los intentos fallaron. Último error: {e}")
                        raise
                except Exception as e:
                    # Para otros errores, no reintentar
                    raise
            raise last_exception
        return wrapper
    return decorator


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

    # Crear cliente Supabase con configuración básica
    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client


