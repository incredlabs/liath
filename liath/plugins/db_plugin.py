from liath.plugin_base import PluginBase
import json

class DBPlugin(PluginBase):
    def initialize(self, context):
        self.db = context['db']
        self.txn = None

    def get_lua_interface(self):
        return {
            'get': self.lua_callable(self.get),
            'put': self.lua_callable(self.put),
            'delete': self.lua_callable(self.delete),
            'begin_transaction': self.lua_callable(self.begin_transaction),
            'commit_transaction': self.lua_callable(self.commit_transaction),
            'rollback_transaction': self.lua_callable(self.rollback_transaction),
            'create_column_family': self.lua_callable(self.create_column_family),
            'drop_column_family': self.lua_callable(self.drop_column_family),
            'list_column_families': self.lua_callable(self.list_column_families),
            'get_cf': self.lua_callable(self.get_cf),
            'put_cf': self.lua_callable(self.put_cf),
            'delete_cf': self.lua_callable(self.delete_cf),
            'iterator': self.lua_callable(self.create_iterator),
            'write_batch': self.lua_callable(self.write_batch),
            'compact_range': self.lua_callable(self.compact_range),
            'flush': self.lua_callable(self.flush),
        }

    def get(self, key):
        return self.db.get(key)

    def put(self, key, value):
        self.db.put(key, value)
        return {"status": "success"}

    def delete(self, key):
        self.db.delete(key)
        return {"status": "success"}

    def begin_transaction(self):
        # Note: Transaction support may vary depending on the storage backend
        if hasattr(self.db, 'transaction'):
            self.txn = self.db.transaction()
            return {"status": "success", "message": "Transaction began"}
        return {"status": "error", "message": "Transactions not supported by this storage backend"}

    def commit_transaction(self):
        if self.txn:
            self.txn.commit()
            self.txn = None
            return {"status": "success", "message": "Transaction committed"}
        return {"status": "error", "message": "No active transaction"}

    def rollback_transaction(self):
        if self.txn:
            self.txn.rollback()
            self.txn = None
            return {"status": "success", "message": "Transaction rolled back"}
        return {"status": "error", "message": "No active transaction"}

    def create_column_family(self, name):
        try:
            self.db.create_column_family(name)
            return {"status": "success", "message": f"Column family '{name}' created"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def drop_column_family(self, name):
        try:
            self.db.drop_column_family(name)
            return {"status": "success", "message": f"Column family '{name}' dropped"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_column_families(self):
        return self.db.list_column_families()

    def get_cf(self, cf_name, key):
        try:
            return self.db.get_cf(cf_name, key)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def put_cf(self, cf_name, key, value):
        try:
            self.db.put_cf(cf_name, key, value)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_cf(self, cf_name, key):
        try:
            self.db.delete_cf(cf_name, key)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_iterator(self, cf_name=None):
        try:
            return self.db.iterator()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def write_batch(self, operations):
        try:
            self.db.write_batch(operations)
            return {"status": "success", "message": f"{len(operations)} operations executed in batch"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def compact_range(self, begin=None, end=None):
        try:
            self.db.compact_range(begin, end)
            return {"status": "success", "message": "Compaction completed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def flush(self):
        try:
            self.db.flush()
            return {"status": "success", "message": "Database flushed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def require_package(self, package_name):
        # Placeholder; Lua require is available from Lua side via configured paths
        return {"status": "error", "message": "Use Lua's require() in queries"}

    @property
    def name(self):
        return "db"
