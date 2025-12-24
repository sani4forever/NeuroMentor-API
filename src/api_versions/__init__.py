"""
This module contains all API versions and
the latest version variable for convenience.

API versions can be added to the `API_VERSIONS` list in any order
because of sorting.
"""

from . import v1

__all__ = [
    'API_LATEST',
    'API_VERSIONS',
    'v1',
]

# You can add various versions to this list in literally random order
# because of sorting, but it is always better, if you add them in
# correct order from the start
API_VERSIONS = sorted([
    v1
], reverse=True, key=lambda v: v.API_VERSION)
API_LATEST = API_VERSIONS[0]
