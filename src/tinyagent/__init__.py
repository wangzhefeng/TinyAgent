"""tinyagent: a self-hosted personal agent with durable runtime capabilities.

Stable surface: ``from tinyagent import ...`` re-exports ``tinyagent.api``.
"""

from .api import *  # noqa: F401,F403
from .api import __all__ as _api_all

__version__ = "1.0.0"

__all__ = [*_api_all, "__version__"]
