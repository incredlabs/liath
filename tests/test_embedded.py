#!/usr/bin/env python3
"""Test embedded usage of Liath."""

import tempfile
import shutil
import os

from liath import EmbeddedLiath


def test_embedded_usage():
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    try:
        db = EmbeddedLiath(data_dir=data_dir, storage_type="leveldb")

        db.put("test_key", "test_value")
        assert db.get("test_key") == "test_value"

        db.set_namespace("test_namespace")
        db.put("namespaced_key", "namespaced_value")
        assert db.get("namespaced_key") == "namespaced_value"

        namespaces = db.list_namespaces()
        assert "default" in namespaces
        assert "test_namespace" in namespaces

        result = db.execute_lua('return "hello from lua"')
        assert result == "hello from lua"

        db.close()
    finally:
        shutil.rmtree(test_dir)

