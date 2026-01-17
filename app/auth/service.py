import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class AuthService:
    """
    Handles authentication-related logic, specifically Token Blacklisting
    using Redis.
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    async def revoke_token(self, jti: str, ttl: int) -> None:
        """
        Revokes a token by adding its JTI (Unique ID) to the Redis blacklist.
        """
        await self.redis.setex(f"blacklist:{jti}", ttl, "logged_out")
        logger.info(f"Token revoked: {jti} (TTL: {ttl}s)")

    async def is_token_revoked(self, jti: str) -> bool:
        """
        Checks if a specific token has been revoked.
        """
        count = await self.redis.exists(f"blacklist:{jti}")
        return count > 0
