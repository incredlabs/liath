#!/usr/bin/env python3
"""
Test script to verify Liath can be used as a library.
"""

import sys
import os
import tempfile
import shutil

# Add the parent directory to the path so we can import liath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from liath import EmbeddedLiath


def test_embedded_usage():
    """Test the embedded usage of Liath."""
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, "data")
    
    # Create the data directory
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # Create an embedded database instance
        db = EmbeddedLiath(data_dir=data_dir, storage_type="leveldb")
        
        # Test basic operations
        db.put("test_key", "test_value")
        retrieved_value = db.get("test_key")
        assert retrieved_value == "test_value", f"Expected 'test_value', got '{retrieved_value}'"
        
        # Test namespace switching
        db.set_namespace("test_namespace")
        db.put("namespaced_key", "namespaced_value")
        namespaced_value = db.get("namespaced_key")
        assert namespaced_value == "namespaced_value", f"Expected 'namespaced_value', got '{namespaced_value}'"
        
        # Test listing namespaces
        namespaces = db.list_namespaces()
        assert "default" in namespaces, "default namespace should exist"
        assert "test_namespace" in namespaces, "test_namespace should exist"
        
        # Test Lua execution
        result = db.execute_lua('return "hello from lua"')
        assert result == "hello from lua", f"Expected 'hello from lua', got '{result}'"
        
        # Close the database
        db.close()
        
        print("All tests passed!")
        
    finally:
        # Clean up the temporary directory
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_embedded_usage()