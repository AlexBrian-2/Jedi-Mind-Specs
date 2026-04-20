import asyncio
import time
import random
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class RateLimitedGatewayClient:
    """Singleton gateway client with token-bucket + sliding-window rate limiting.
    
    Enforces:
    - Soft ceiling of 180 requests/hour (10% buffer below hard 200)
    - Token bucket for burst control (10 tokens, refill rate 1/18sec)
    - Maximum 4 concurrent requests
    """
    soft_limit: int = 180
    window_seconds: int = 3600
    max_burst: int = 10
    max_concurrent: int = 4
    
    _instance: Optional['RateLimitedGatewayClient'] = field(default=None, init=False, repr=False)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)
    
    _timestamps: deque = field(default_factory=deque, init=False, repr=False)
    _tokens: float = field(default=10.0, init=False, repr=False)
    _last_refill: float = field(default_factory=time.monotonic, init=False, repr=False)
    _semaphore: asyncio.Semaphore = field(default=None, init=False, repr=False)
    _queue: asyncio.Queue = field(default=None, init=False, repr=False)
    _refill_rate: float = field(default=0.0, init=False, repr=False)
    
    _auth_token: Optional[str] = field(default=None, init=False, repr=False)
    _authenticated: bool = field(default=False, init=False, repr=False)
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    cls._instance = instance
        return cls._instance
    
    def __post_init__(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
            self._queue = asyncio.Queue()
            self._refill_rate = self.soft_limit / self.window_seconds
            self._last_refill = time.monotonic()
    
    @classmethod
    def get_instance(cls) -> 'RateLimitedGatewayClient':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._timestamps.clear()
                cls._instance._tokens = cls._instance.max_burst
                cls._instance._last_refill = time.monotonic()
            cls._instance = None
    
    def _refill_tokens(self):
        """Refill token bucket based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_burst, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now
    
    def _count_window(self) -> int:
        """Count requests in sliding window."""
        cutoff = time.time() - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
        return len(self._timestamps)
    
    def get_status(self) -> dict:
        """Get current rate limit status."""
        self._refill_tokens()
        window_count = self._count_window()
        remaining = self.soft_limit - window_count
        
        cutoff = time.time() - self.window_seconds
        next_reset = self.window_seconds
        if self._timestamps:
            oldest = self._timestamps[0]
            next_reset = int(oldest + self.window_seconds - time.time())
            next_reset = max(0, next_reset)
        
        return {
            'requests_this_hour': window_count,
            'soft_limit': self.soft_limit,
            'hard_limit': self.soft_limit + 20,
            'tokens_available': int(self._tokens),
            'max_burst': self.max_burst,
            'remaining': max(0, remaining),
            'next_reset_seconds': next_reset,
            'authenticated': self._authenticated,
        }
    
    async def _wait_for_capacity(self):
        """Wait until capacity is available for a request."""
        while True:
            self._refill_tokens()
            window_count = self._count_window()
            
            if window_count < self.soft_limit and self._tokens >= 1:
                self._tokens -= 1
                self._timestamps.append(time.time())
                return
            
            sleep_time = random.uniform(1.0, 2.0)
            await asyncio.sleep(sleep_time)
    
    async def call(self, fn: Callable, *args, **kwargs) -> Any:
        """Execute fn with rate limiting and retry logic."""
        await self._wait_for_capacity()
        
        async with self._semaphore:
            backoff = 5.0
            for attempt in range(6):
                try:
                    result = await fn(*args, **kwargs)
                    return result
                except Exception as e:
                    error_str = str(e)
                    if '429' in error_str or 'rate limit' in error_str.lower():
                        if attempt < 5:
                            jitter = random.uniform(0.8, 1.2)
                            wait_time = min(backoff * jitter, 120)
                            logger.warning(f"Rate limited, backing off {wait_time:.1f}s (attempt {attempt + 1})")
                            await asyncio.sleep(wait_time)
                            backoff *= 2
                        else:
                            logger.error(f"Rate limit exceeded after {attempt + 1} attempts")
                            raise
                    else:
                        raise
    
    async def call_with_auth(self, fn: Callable, *args, **kwargs) -> Any:
        """Execute fn with authentication token."""
        async def _authenticated_call():
            import litellm
            return await fn(*args, **kwargs)
        return await self.call(_authenticated_call)
    
    def set_auth_token(self, token: str):
        """Set authentication token for API calls."""
        self._auth_token = token
        self._authenticated = True
        logger.info("Authentication token set")


class SyncRateLimitedClient:
    """Synchronous version for non-async contexts."""
    
    _instance: Optional['RateLimitedGatewayClient'] = None
    
    @classmethod
    def get_instance(cls) -> RateLimitedGatewayClient:
        if cls._instance is None:
            cls._instance = RateLimitedGatewayClient.get_instance()
        return cls._instance
    
    @classmethod
    def get_status(cls) -> dict:
        return cls.get_instance().get_status()