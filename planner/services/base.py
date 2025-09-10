import logging
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common functionality"""
    
    def __init__(self):
        self.cache_ttl = getattr(settings, 'CACHE_TTL', 3600)
    
    def get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache"""
        try:
            return cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get error for key {cache_key}: {e}")
            return None
    
    def set_cache(self, cache_key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache"""
        try:
            cache.set(cache_key, data, ttl or self.cache_ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {cache_key}: {e}")
            return False
    
    def log_error(self, message: str, exception: Exception = None):
        """Log error with context"""
        if exception:
            logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            logger.error(message)
    
    def log_warning(self, message: str):
        """Log warning"""
        logger.warning(message)
    
    def log_info(self, message: str):
        """Log info"""
        logger.info(message)
