try:
    import rocksdb
except:
    print("Please install the 'rocksdb' package")
    
from .base import StorageBase

class RocksDBStorage(StorageBase):
    def __init__(self, path, options=None):
        if options is None:
            opts = rocksdb.Options()
            opts.create_if_missing = True
            opts.max_open_files = 300000
            opts.write_buffer_size = 67108864
            opts.max_write_buffer_number = 3
            opts.target_file_size_base = 67108864

            opts.table_factory = rocksdb.BlockBasedTableFactory(
                filter_policy=rocksdb.BloomFilterPolicy(10),
                block_cache=rocksdb.LRUCache(2 * (1024 ** 3)),
                block_cache_compressed=rocksdb.LRUCache(500 * (1024 ** 2)))

            opts.compression = rocksdb.CompressionType.lz4_compression
            opts.compaction_style = rocksdb.CompactionStyle.level
        self.db = rocksdb.DB(path, opts)
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
        iter = self.db.iteritems()
        iter.seek_to_first()
        items = []
        for key, value in iter:
            items.append({key.decode('utf-8'): value.decode('utf-8')})
        return items

    def write_batch(self, operations):
        batch = rocksdb.WriteBatch()
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
        return self.db.write(batch)

    def create_column_family(self, name):
        cf_opts = rocksdb.ColumnFamilyOptions()
        self.column_families[name] = self.db.create_column_family(cf_opts, name)

    def drop_column_family(self, name):
        if name in self.column_families:
            self.db.drop_column_family(self.column_families[name])
            del self.column_families[name]

    def list_column_families(self):
        return list(self.column_families.keys())

    def get_cf(self, cf_name, key):
        if cf_name in self.column_families:
            if isinstance(key, str):
                key = key.encode('utf-8')
            result = self.db.get(key, column_family=self.column_families[cf_name])
            return result.decode('utf-8') if result else None
        raise ValueError(f"Column family '{cf_name}' not found")

    def put_cf(self, cf_name, key, value):
        if cf_name in self.column_families:
            if isinstance(key, str):
                key = key.encode('utf-8')
            if isinstance(value, str):
                value = value.encode('utf-8')
            return self.db.put(key, value, column_family=self.column_families[cf_name])
        raise ValueError(f"Column family '{cf_name}' not found")

    def delete_cf(self, cf_name, key):
        if cf_name in self.column_families:
            if isinstance(key, str):
                key = key.encode('utf-8')
            return self.db.delete(key, column_family=self.column_families[cf_name])
        raise ValueError(f"Column family '{cf_name}' not found")

    def compact_range(self, begin, end):
        if isinstance(begin, str):
            begin = begin.encode('utf-8')
        if isinstance(end, str):
            end = end.encode('utf-8')
        return self.db.compact_range(begin, end)

    def flush(self):
        return self.db.flush()

    def close(self):
        del self.db