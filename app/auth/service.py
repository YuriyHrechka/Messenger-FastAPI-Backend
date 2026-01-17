from redis.asyncio import Redis


class AuthService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def revoke_token(self, jti: str, ttl: int) -> None:
        await self.redis.setex(f"blacklist:{jti}", ttl, "logged_out")

    async def is_token_revoked(self, jti: str) -> bool:
        count = await self.redis.exists(f"blacklist:{jti}")
        return count > 0
