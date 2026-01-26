"""
Abstract base class for storage backends.

This module defines the interface that all storage backends must implement.
"""

from abc import ABC, abstractmethod


class StorageBase(ABC):
    """Abstract base class for Liath storage backends.

    All storage backends (RocksDB, LevelDB, etc.) must inherit from this
    class and implement all abstract methods.

    Storage backends provide:
    - Basic CRUD operations (get, put, delete)
    - Batch writes for atomic operations
    - Iteration over all keys
    - Column family support (logical partitioning)
    - Maintenance operations (compaction, flush)
    """

    @abstractmethod
    def get(self, key):
        """Retrieve a value by key.

        Args:
            key: The key to look up (string or bytes).

        Returns:
            The value as a string, or None if the key doesn't exist.
        """
        pass

    @abstractmethod
    def put(self, key, value):
        """Store a value with the given key.

        Args:
            key: The key to store (string or bytes).
            value: The value to store (string or bytes).
        """
        pass

    @abstractmethod
    def delete(self, key):
        """Delete a key and its value.

        Args:
            key: The key to delete (string or bytes).
        """
        pass

    @abstractmethod
    def iterator(self):
        """Iterate over all key-value pairs.

        Returns:
            List of dicts, each containing a single {key: value} pair.
        """
        pass

    @abstractmethod
    def write_batch(self, operations):
        """Execute multiple operations atomically.

        Args:
            operations: List of operation dicts. Each dict should have:
                - 'type': 'put' or 'delete'
                - 'key': The key to operate on
                - 'value': The value (for 'put' operations only)

        Example:
            >>> storage.write_batch([
            ...     {'type': 'put', 'key': 'k1', 'value': 'v1'},
            ...     {'type': 'delete', 'key': 'k2'}
            ... ])
        """
        pass

    @abstractmethod
    def create_column_family(self, name):
        """Create a new column family (logical partition).

        Args:
            name: Name for the column family.

        Note:
            Column families provide logical separation of data within
            a single database.
        """
        pass

    @abstractmethod
    def drop_column_family(self, name):
        """Delete a column family and all its data.

        Args:
            name: Name of the column family to drop.
        """
        pass

    @abstractmethod
    def list_column_families(self):
        """List all column family names.

        Returns:
            List of column family name strings.
        """
        pass

    @abstractmethod
    def get_cf(self, cf_name, key):
        """Get a value from a column family.

        Args:
            cf_name: Name of the column family.
            key: The key to look up.

        Returns:
            The value as a string, or None if not found.

        Raises:
            ValueError: If the column family doesn't exist.
        """
        pass

    @abstractmethod
    def put_cf(self, cf_name, key, value):
        """Store a value in a column family.

        Args:
            cf_name: Name of the column family.
            key: The key to store.
            value: The value to store.

        Raises:
            ValueError: If the column family doesn't exist.
        """
        pass

    @abstractmethod
    def delete_cf(self, cf_name, key):
        """Delete a key from a column family.

        Args:
            cf_name: Name of the column family.
            key: The key to delete.

        Raises:
            ValueError: If the column family doesn't exist.
        """
        pass

    @abstractmethod
    def compact_range(self, begin, end):
        """Compact data in a key range (RocksDB only).

        Args:
            begin: Start key of the range.
            end: End key of the range.

        Note:
            This is a no-op for backends that don't support compaction.
        """
        pass

    @abstractmethod
    def flush(self):
        """Flush in-memory data to disk (RocksDB only).

        Note:
            This is a no-op for backends that don't support explicit flushing.
        """
        pass

    @abstractmethod
    def close(self):
        """Close the database and release resources.

        Should be called when the storage is no longer needed.
        """
        pass