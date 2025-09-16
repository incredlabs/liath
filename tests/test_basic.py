#!/usr/bin/env python3

from liath.database import Database


def test_basic_functionality():
    db = Database(data_dir='./test_data', storage_type='leveldb')
    db.create_namespace('test')

    db.namespaces['test']['db'].put('test_key', 'test_value')
    value = db.namespaces['test']['db'].get('test_key')
    assert value == 'test_value'

    namespaces = db.list_namespaces()
    assert 'test' in namespaces

    db.close()

