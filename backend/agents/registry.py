from typing import Dict, Type

# Registry dict — populated by @register decorator
_registry: Dict[str, type] = {}

def register(cls):
    """Decorator — add to any AgentNode subclass to self-register."""
    _registry[cls.name] = cls
    return cls

def get_agent(name: str):
    if name not in _registry:
        raise ValueError(f"Agent '{name}' not found. Registered: {list(_registry)}")
    return _registry[name]()

def list_agents() -> list:
    return [
        {
            "name":  name,
            "class": cls.__name__,
            "doc":   (cls.__doc__ or "").strip(),
        }
        for name, cls in _registry.items()
    ]