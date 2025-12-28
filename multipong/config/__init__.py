"""
multipong/config/ – Konfigurační systém MULTIPONG.

Spravuje načítání a zpřístupnění nastavení hry z config.json.
"""

from multipong.config.config_loader import load_config, get

__all__ = ["load_config", "get"]
