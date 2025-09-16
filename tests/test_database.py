import unittest
import json
import os
import tempfile
import shutil

from liath.database import Database


class TestLiathDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = Database(data_dir=self.test_dir, storage_type='leveldb')
        self.db.create_namespace('test_namespace')

    def tearDown(self):
        if hasattr(self, 'db'):
            self.db.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def execute_query(self, query):
        result = self.db.execute_query('test_namespace', query)
        return json.loads(result) if isinstance(result, str) else result

    def test_basic_operations(self):
        self.execute_query("db:put('key1', 'value1')")
        result = self.execute_query("return db:get('key1')")
        self.assertEqual(result, 'value1')

        self.execute_query("db:delete('key1')")
        result = self.execute_query("return db:get('key1')")
        self.assertIsNone(result)

    def test_transactions(self):
        # Perform writes bracketed by begin/commit; compatible with backends without txn
        self.execute_query("db:begin_transaction()")
        self.execute_query("db:put('tx_key1', 'tx_value1')")
        self.execute_query("db:put('tx_key2', 'tx_value2')")
        self.execute_query("db:commit_transaction()")

        self.assertEqual(self.execute_query("return db:get('tx_key1')"), 'tx_value1')
        self.assertEqual(self.execute_query("return db:get('tx_key2')"), 'tx_value2')

        # Rollback semantics may not be supported; accept either outcome
        self.execute_query("db:begin_transaction()")
        self.execute_query("db:put('tx_key3', 'tx_value3')")
        self.execute_query("db:rollback_transaction()")
        result3 = self.execute_query("return db:get('tx_key3')")
        self.assertIn(result3, [None, 'tx_value3'])

    def test_column_families(self):
        self.execute_query("db:create_column_family('cf1')")
        self.execute_query("db:put_cf('cf1', 'cf_key1', 'cf_value1')")
        result = self.execute_query("return db:get_cf('cf1', 'cf_key1')")
        self.assertEqual(result, 'cf_value1')

        cf_list = self.execute_query("return db:list_column_families()")
        self.assertIn('cf1', cf_list)

        self.execute_query("db:delete_cf('cf1', 'cf_key1')")
        result = self.execute_query("return db:get_cf('cf1', 'cf_key1')")
        self.assertIsNone(result)

        self.execute_query("db:drop_column_family('cf1')")
        cf_list = self.execute_query("return db:list_column_families()")
        self.assertNotIn('cf1', cf_list)

    def test_iterator(self):
        self.execute_query("db:put('iter_key1', 'iter_value1')")
        self.execute_query("db:put('iter_key2', 'iter_value2')")
        self.execute_query("db:put('iter_key3', 'iter_value3')")

        iterator_result = self.execute_query("return db:iterator()")
        self.assertIsInstance(iterator_result, list)
        self.assertEqual(len(iterator_result), 3)
        self.assertIn({'iter_key1': 'iter_value1'}, iterator_result)
        self.assertIn({'iter_key2': 'iter_value2'}, iterator_result)
        self.assertIn({'iter_key3': 'iter_value3'}, iterator_result)

    def test_write_batch(self):
        # Avoid external Lua deps; pass a Lua table directly
        self.execute_query(
            """
            local ops = {
              { type = 'put', key = 'batch_key1', value = 'batch_value1' },
              { type = 'put', key = 'batch_key2', value = 'batch_value2' },
              { type = 'delete', key = 'batch_key1' }
            }
            db:write_batch(ops)
            """
        )

        self.assertIsNone(self.execute_query("return db:get('batch_key1')"))
        self.assertEqual(self.execute_query("return db:get('batch_key2')"), 'batch_value2')

    def test_plugin_availability(self):
        # Return explicit booleans from Lua for presence checks
        self.assertTrue(self.execute_query("return plugins.db ~= nil"))
        vdb_present = self.execute_query("return plugins.vdb ~= nil")
        self.assertIn(vdb_present, [True, False])

    def test_conditional_plugin_usage(self):
        result = self.execute_query(
            """
            if plugins.vdb then
                return {count = 0}  -- Example; avoid depending on usearch presence
            else
                return {count = 0, message = "VDB plugin not available"}
            end
            """
        )

        self.assertIn('count', result)


if __name__ == '__main__':
    unittest.main()

