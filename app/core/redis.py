# app/core/redis.py
import redis.asyncio as redis
from app.core.config import settings # Assuming you store REDIS_URL here

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis_client():
    """Dependency to get the Redis client."""
    return redis_client

# Example use in an endpoint:
# @router.get("/dashboard/")
# async def get_dashboard_data(r: redis.Redis = Depends(get_redis_client)):
#     cached_data = await r.get("dashboard_data:user_id")
#     if cached_data:
#         return json.loads(cached_data)
#     # ... fetch from Postgres, then r.set() ...