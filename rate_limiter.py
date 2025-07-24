"""
Rate limiting functionality to prevent API abuse.
"""
import time
from collections import defaultdict, deque
from config import RATE_LIMIT_MESSAGES, RATE_LIMIT_WINDOW


class RateLimiter:
    """Simple rate limiter using sliding window approach."""
    
    def __init__(self):
        # Store message timestamps for each user
        self.user_messages = defaultdict(deque)
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user is allowed to send a message based on rate limits.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is within rate limits, False otherwise
        """
        current_time = time.time()
        user_queue = self.user_messages[user_id]
        
        # Remove old messages outside the time window
        while user_queue and current_time - user_queue[0] > RATE_LIMIT_WINDOW:
            user_queue.popleft()
        
        # Check if user has exceeded rate limit
        if len(user_queue) >= RATE_LIMIT_MESSAGES:
            return False
        
        # Add current message timestamp
        user_queue.append(current_time)
        return True
    
    def get_user_message_count(self, user_id: int) -> int:
        """Get current message count for a user within the time window."""
        current_time = time.time()
        user_queue = self.user_messages[user_id]
        
        # Remove old messages outside the time window
        while user_queue and current_time - user_queue[0] > RATE_LIMIT_WINDOW:
            user_queue.popleft()
        
        return len(user_queue)
    
    def reset_user_limit(self, user_id: int) -> None:
        """Reset rate limit for a specific user (admin function)."""
        if user_id in self.user_messages:
            self.user_messages[user_id].clear()
