"""
Storage backends for Liath database.

This package provides storage backend implementations:
- base: Abstract base class (StorageBase)
- leveldb_storage: LevelDB backend (default)
- rocksdb_storage: RocksDB backend (requires liath[rocksdb])
"""

from .base import StorageBase
from .leveldb_storage import LevelDBStorage

__all__ = ['StorageBase', 'LevelDBStorage']

# Conditionally export RocksDB storage if available
try:
    from .rocksdb_storage import RocksDBStorage
    __all__.append('RocksDBStorage')
except ImportError:
    pass
