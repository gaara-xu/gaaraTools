import pkgutil
import importlib
from typing import Callable, Dict

FEATURE_REGISTRY: Dict[str, Callable] = {}


def register_feature(name: str):
    """Decorator to register a feature builder."""
    def decorator(func: Callable) -> Callable:
        FEATURE_REGISTRY[name] = func
        return func
    return decorator


def load_features() -> Dict[str, Callable]:
    """Import all modules under this package and return the registry."""
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")
    return FEATURE_REGISTRY
