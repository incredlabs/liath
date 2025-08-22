"""
Embedded Liath Database Interface

This module provides a simplified interface for embedding Liath directly into Python applications.
"""

from typing import Any, Dict, List, Optional, Union
from .database import Database


class EmbeddedLiath:
    """
    A simplified interface for embedding Liath in Python applications.
    
    This class provides a high-level API for common database operations
    without needing to write Lua queries.
    """
    
    def __init__(self, data_dir: str = "./data", storage_type: str = "auto"):
        """
        Initialize the embedded Liath database.
        
        Args:
            data_dir: Directory to store database files
            storage_type: Storage backend ('auto', 'rocksdb', or 'leveldb')
        """
        self.db = Database(data_dir=data_dir, storage_type=storage_type)
        # Create default namespace if it doesn't exist
        if 'default' not in self.db.list_namespaces():
            self.db.create_namespace('default')
        self.current_namespace = 'default'
    
    def set_namespace(self, namespace: str) -> None:
        """
        Switch to a different namespace.
        
        Args:
            namespace: Name of the namespace to switch to
        """
        if namespace not in self.db.list_namespaces():
            self.db.create_namespace(namespace)
        self.current_namespace = namespace
    
    def put(self, key: str, value: str) -> None:
        """
        Store a key-value pair in the database.
        
        Args:
            key: Key to store
            value: Value to store
        """
        self.db.namespaces[self.current_namespace]['db'].put(key, value)
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from the database.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Value associated with the key, or None if not found
        """
        return self.db.namespaces[self.current_namespace]['db'].get(key)
    
    def delete(self, key: str) -> None:
        """
        Delete a key-value pair from the database.
        
        Args:
            key: Key to delete
        """
        self.db.namespaces[self.current_namespace]['db'].delete(key)
    
    def execute_lua(self, query: str) -> Any:
        """
        Execute a Lua query.
        
        Args:
            query: Lua query to execute
            
        Returns:
            Result of the query execution
        """
        return self.db.execute_query(self.current_namespace, query)
    
    def create_user(self, username: str, password: str) -> None:
        """
        Create a new user.
        
        Args:
            username: Username
            password: Password
        """
        self.db.create_user(username, password)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            True if authentication successful, False otherwise
        """
        return self.db.authenticate_user(username, password)
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespaces.
        
        Returns:
            List of namespace names
        """
        return self.db.list_namespaces()
    
    def close(self) -> None:
        """
        Close the database connection.
        """
        self.db.close()


def create_embedded_liath(data_dir: str = "./data", storage_type: str = "auto") -> EmbeddedLiath:
    """
    Factory function to create an embedded Liath instance.
    
    Args:
        data_dir: Directory to store database files
        storage_type: Storage backend ('auto', 'rocksdb', or 'leveldb')
        
    Returns:
        EmbeddedLiath instance
    """
    return EmbeddedLiath(data_dir=data_dir, storage_type=storage_type)