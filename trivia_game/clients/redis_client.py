import logging
import os

import redis

from utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)

logger.info("Connecting to Redis at %s:%s", REDIS_HOST, REDIS_PORT)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)