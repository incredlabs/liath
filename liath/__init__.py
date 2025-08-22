"""
Liath: An AI-powered database system with key-value storage, vector search, and AI capabilities.

This package provides:
- A database system with pluggable storage backends (RocksDB/LevelDB)
- Lua as the query language
- Plugin architecture for extensibility
- CLI and HTTP API interfaces
- AI integration capabilities
"""

from .database import Database
from .cli import DatabaseCLI
from .cli_entry import main as cli_main
from .server import create_app, run_server
from .embedded import EmbeddedLiath, create_embedded_liath

__version__ = "0.1.0"
__author__ = "Dipankar Sarkar"
__email__ = "me@dipankar.name"