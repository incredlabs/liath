#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from liath.database import Database

def test_basic_functionality():
    # Create a database instance with LevelDB (more portable)
    db = Database(data_dir='./test_data', storage_type='leveldb')
    
    # Create a test namespace
    db.create_namespace('test')
    
    # Test basic put/get operations
    db.namespaces['test']['db'].put('test_key', 'test_value')
    value = db.namespaces['test']['db'].get('test_key')
    
    print(f"Retrieved value: {value}")
    
    # Test list namespaces
    namespaces = db.list_namespaces()
    print(f"Namespaces: {namespaces}")
    
    # Close the database
    db.close()
    
    print("Basic functionality test passed!")

if __name__ == "__main__":
    test_basic_functionality()