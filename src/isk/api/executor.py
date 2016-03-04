"""
As long Isk API is blocking, we need to run its calls with executor.
"""

# TODO: Use process pool
from concurrent.futures import ThreadPoolExecutor


MAX_SIMULTANEOUS_ISK_API_CALLS = 1  # No diff with ThreadPoolExecutor, migrate to Process pool


isk_api_executor = ThreadPoolExecutor(max_workers=MAX_SIMULTANEOUS_ISK_API_CALLS)
