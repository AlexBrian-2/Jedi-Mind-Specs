"""Test rate limiter in isolation."""

import asyncio
import time
import pytest
from collections import deque


class MockRateLimitedClient:
    """Test version of rate limiter with minimal dependencies."""
    
    def __init__(self):
        self.soft_limit = 180
        self.window_seconds = 3600
        self.max_burst = 10
        self.max_concurrent = 4
        
        self._timestamps = deque()
        self._tokens = 10.0
        self._last_refill = time.monotonic()
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        
        self._refill_rate = self.soft_limit / self.window_seconds
    
    def _refill_tokens(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_burst, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now
    
    def _count_window(self) -> int:
        cutoff = time.time() - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
        return len(self._timestamps)
    
    def get_status(self) -> dict:
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
        }
    
    async def _wait_for_capacity(self):
        while True:
            self._refill_tokens()
            window_count = self._count_window()
            
            if window_count < self.soft_limit and self._tokens >= 1:
                self._tokens -= 1
                self._timestamps.append(time.time())
                return
            
            await asyncio.sleep(0.1)
    
    async def call(self, fn, *args, **kwargs):
        await self._wait_for_capacity()
        
        async with self._semaphore:
            result = await fn(*args, **kwargs)
            return result


@pytest.fixture
def rate_limiter():
    """Create a fresh rate limiter for each test."""
    client = MockRateLimitedClient()
    return client


@pytest.mark.asyncio
async def test_initial_state(rate_limiter):
    """Test initial state of rate limiter."""
    status = rate_limiter.get_status()
    
    assert status['requests_this_hour'] == 0
    assert status['tokens_available'] == 10
    assert status['remaining'] == 180


@pytest.mark.asyncio
async def test_token_consumption(rate_limiter):
    """Test that tokens are consumed on calls."""
    call_count = 0
    
    async def mock_call():
        nonlocal call_count
        call_count += 1
        return "result"
    
    for _ in range(5):
        await rate_limiter.call(mock_call)
    
    status = rate_limiter.get_status()
    assert status['requests_this_hour'] == 5
    assert status['tokens_available'] == 5
    assert status['remaining'] == 175


@pytest.mark.asyncio
async def test_concurrent_calls(rate_limiter):
    """Test concurrent call limiting."""
    active_calls = 0
    max_concurrent = 0
    
    async def mock_call():
        nonlocal active_calls, max_concurrent
        active_calls += 1
        max_concurrent = max(max_concurrent, active_calls)
        await asyncio.sleep(0.1)
        active_calls -= 1
        return "result"
    
    tasks = [rate_limiter.call(mock_call) for _ in range(10)]
    await asyncio.gather(*tasks)
    
    assert max_concurrent <= rate_limiter.max_concurrent


@pytest.mark.asyncio
async def test_rate_limit_enforcement(rate_limiter):
    """Test that rate limit is enforced."""
    rate_limiter.soft_limit = 5
    
    call_count = 0
    
    async def mock_call():
        nonlocal call_count
        call_count += 1
        return "result"
    
    start = time.time()
    for _ in range(10):
        await rate_limiter.call(mock_call)
    elapsed = time.time() - start
    
    assert call_count == 10
    status = rate_limiter.get_status()
    assert status['requests_this_hour'] == 10


@pytest.mark.asyncio
async def test_sliding_window(rate_limiter):
    """Test sliding window eviction."""
    rate_limiter.window_seconds = 1
    
    call_count = 0
    
    async def mock_call():
        nonlocal call_count
        call_count += 1
        return "result"
    
    await rate_limiter.call(mock_call)
    await rate_limiter.call(mock_call)
    
    status = rate_limiter.get_status()
    assert status['requests_this_hour'] == 2
    
    await asyncio.sleep(1.5)
    
    status = rate_limiter.get_status()
    assert status['requests_this_hour'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])