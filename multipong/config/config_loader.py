"""
config_loader.py – Načítač konfigurace pro MULTIPONG.

Zpřístupňuje bezpečné čtení konfiguračních parametrů z config.json.
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

# Globální cache konfigurace
CONFIG: dict = {}


def load_config() -> dict:
    """
    Načte config.json do globální proměnné CONFIG.
    
    Returns:
        dict: Načtená konfigurace
    """
    global CONFIG

    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
        logger.info(f"✅ Konfigurace načtena z {config_path}")
        return CONFIG
    except FileNotFoundError:
        logger.error(f"❌ Konfigurační soubor nenalezen: {config_path}")
        CONFIG = {}
        return CONFIG
    except json.JSONDecodeError as e:
        logger.error(f"❌ Chyba při parsování JSON: {e}")
        CONFIG = {}
        return CONFIG


def get(path: str, default=None):
    """
    Bezpečné získání hodnoty z konfigurace.
    
    Path ve tvaru 'section.key' nebo 'section.subsection.key'
    
    Args:
        path: Cesta ke konfigurační hodnotě (např. 'ball.radius')
        default: Výchozí hodnota, pokud cesta neexistuje
    
    Returns:
        Hodnota z konfigurace nebo default
    
    Examples:
        >>> get("ball.radius")
        10
        >>> get("nonexistent.key", 42)
        42
    """
    if not CONFIG:
        logger.warning("⚠️ Konfigurace není načtena. Volejte load_config() nejprve.")
        return default
    
    parts = path.split(".")
    value = CONFIG
    
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            logger.debug(f"⚠️ Konfigurační cesta '{path}' neexistuje, vrácena výchozí hodnota: {default}")
            return default
    
    return value


def get_all() -> dict:
    """
    Vrátí celou načtenou konfiguraci.
    
    Returns:
        dict: Celá konfigurace
    """
    if not CONFIG:
        logger.warning("⚠️ Konfigurace není načtena.")
    return CONFIG.copy()
