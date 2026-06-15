"""
SOAR Connector Hub — Connector Registry
=======================================
Central registry that loads, initializes, and manages all connectors.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Type

from app.core.base_connector import BaseConnector
from app.core.exceptions import ConfigurationError

logger = logging.getLogger("soar.registry")


class ConnectorRegistry:
    """
    Maintains a map of connector_name -> connector class.
    Supports dynamic loading and instance caching per config.
    """

    _connector_classes: Dict[str, Type[BaseConnector]] = {}

    @classmethod
    def register(cls, connector_class: Type[BaseConnector]) -> None:
        name = connector_class.NAME
        if not name:
            raise ValueError(f"Connector {connector_class.__name__} has no NAME defined.")
        cls._connector_classes[name] = connector_class
        logger.info("Registered connector: %s v%s", name, connector_class.VERSION)

    @classmethod
    def get_class(cls, name: str) -> Type[BaseConnector]:
        klass = cls._connector_classes.get(name)
        if not klass:
            raise ConfigurationError(f"Connector '{name}' is not registered.")
        return klass

    @classmethod
    def list_connectors(cls) -> List[Dict]:
        return [
            {
                "name": klass.NAME,
                "version": klass.VERSION,
                "description": klass.DESCRIPTION,
            }
            for klass in cls._connector_classes.values()
        ]

    @classmethod
    def create_instance(cls, name: str, config: dict) -> BaseConnector:
        """Create a fresh connector instance with the given config."""
        klass = cls.get_class(name)
        return klass(config)


def _load_all_connectors() -> None:
    """Import all connector modules dynamically so they self-register."""
    import importlib
    from pathlib import Path

    connectors_dir = Path(__file__).parent.parent / "connectors"
    print(f"[DEBUG] Searching for connectors in: {connectors_dir}")
    if not connectors_dir.exists():
        print("[DEBUG] Directory does not exist!")
    for item in connectors_dir.iterdir():
        if item.is_dir() and (item / "connector.py").exists():
            module_path = f"app.connectors.{item.name}.connector"
            print(f"[DEBUG] Found connector module: {module_path}")
            try:
                importlib.import_module(module_path)
            except ImportError as e:
                logger.warning("Could not load connector module %s: %s", module_path, e)


# Auto-load on import
_load_all_connectors()
