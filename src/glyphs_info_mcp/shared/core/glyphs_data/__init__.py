#!/usr/bin/env python3
"""
Glyphs Data - Unified data access interface

Converts all JSON data into directly importable Python objects
"""

# mypy: ignore-errors

from . import handbook, plugins, python_api

__all__ = ["python_api", "plugins", "handbook"]
