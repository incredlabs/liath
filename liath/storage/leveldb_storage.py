import plyvel
from .base import StorageBase

class LevelDBStorage(StorageBase):
    def __init__(self, path, options=None):
        self.db = plyvel.DB(path, create_if_missing=True)
        self.column_families = {}

    def get(self, key):
        if isinstance(key, str):
            key = key.encode('utf-8')
        result = self.db.get(key)
        return result.decode('utf-8') if result else None

    def put(self, key, value):
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        return self.db.put(key, value)

    def delete(self, key):
        if isinstance(key, str):
            key = key.encode('utf-8')
        return self.db.delete(key)

    def iterator(self):
        items = []
        for key, value in self.db:
            items.append({key.decode('utf-8'): value.decode('utf-8')})
        return items

    def write_batch(self, operations):
        with self.db.write_batch() as batch:
            for op in operations:
                if isinstance(op['key'], str):
                    op['key'] = op['key'].encode('utf-8')
                if op['type'] == 'put':
                    value = op['value']
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    batch.put(op['key'], value)
                elif op['type'] == 'delete':
                    batch.delete(op['key'])

    def create_column_family(self, name):
        self.column_families[name] = self.db.prefixed_db(name.encode('utf-8') + b':')

    def drop_column_family(self, name):
        if name in self.column_families:
            # LevelDB doesn't have built-in column families, so we need to manually delete all keys
            prefix = name.encode('utf-8') + b':'
            with self.db.write_batch() as batch:
                for key, _ in self.db.iterator(prefix=prefix):
                    batch.delete(key)
            del self.column_families[name]

    def list_column_families(self):
        return list(self.column_families.keys())

    def get_cf(self, cf_name, key):
        if cf_name in self.column_families:
            if isinstance(key, str):
                key = key.encode('utf-8')
            result = self.column_families[cf_name].get(key)
            return result.decode('utf-8') if result else None
        raise ValueError(f"Column family '{cf_name}' not found")

    def put_cf(self, cf_name, key, value):
        if cf_name in self.column_families:
            if isinstance(key, str):
                key = key.encode('utf-8')
            if isinstance(value, str):
                value = value.encode('utf-8')
            return self.column_families[cf_name].put(key, value)
        raise ValueError(f"Column family '{cf_name}' not found")

    def delete_cf(self, cf_name, key):
        if cf_name in self.column_families:
            if isinstance(key, str):
                key = key.encode('utf-8')
            return self.column_families[cf_name].delete(key)
        raise ValueError(f"Column family '{cf_name}' not found")

    def compact_range(self, begin, end):
        # LevelDB doesn't have a direct compact_range method
        pass

    def flush(self):
        # LevelDB doesn't have a direct flush method
        pass

    def close(self):
        self.db.close()