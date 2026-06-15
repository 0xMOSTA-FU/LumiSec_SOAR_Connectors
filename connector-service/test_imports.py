import os
import sys

# Ensure the app module can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app.main import app
    from app.core.registry import ConnectorRegistry
    print(f"[OK] Core Engine loaded successfully!")
    print(f"[OK] Total Connectors Discovered: {len(ConnectorRegistry._connector_classes)}")
    for name in ConnectorRegistry._connector_classes.keys():
        print(f"  - {name}")
    print("[OK] All modules have correct syntax and imports.")
except Exception as e:
    print(f"[ERROR] Error loading the application: {e}")
    sys.exit(1)
