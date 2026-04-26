"""Wrapper de Redis para cache de datos en vivo y rate limiting."""

import json
import logging

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

_pool: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    """Singleton de conexión Redis. Retorna None si no está configurado."""
    global _pool
    if _pool is None:
        if not settings.redis_url:
            return None
        _pool = redis.from_url(settings.redis_url, decode_responses=True)
    return _pool


async def cache_get(clave: str) -> dict | None:
    """Obtiene un valor del cache. Funciona sin Redis (siempre miss)."""
    r = get_redis()
    if r is None:
        return None
    try:
        valor = await r.get(clave)
        if valor:
            return json.loads(valor)
    except Exception:
        logger.warning("Error leyendo cache para %s", clave)
    return None


async def cache_set(clave: str, valor: dict, ttl_segundos: int = 3600) -> None:
    """Guarda un valor en cache con TTL. No-op si Redis no está configurado."""
    r = get_redis()
    if r is None:
        return
    try:
        await r.set(clave, json.dumps(valor, ensure_ascii=False), ex=ttl_segundos)
    except Exception:
        logger.warning("Error escribiendo cache para %s", clave)


async def verificar_rate_limit(ip: str) -> bool:
    """Verifica si una IP ha excedido el rate limit. Sin Redis, siempre permite."""
    r = get_redis()
    if r is None:
        return True
    clave = f"rate_limit:{ip}"
    try:
        count = await r.incr(clave)
        if count == 1:
            await r.expire(clave, 60)
        return count <= settings.rate_limit_per_min
    except Exception:
        logger.warning("Error verificando rate limit para %s", ip)
        return True
