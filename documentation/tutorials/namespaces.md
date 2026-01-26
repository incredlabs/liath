# Using Namespaces

Namespaces provide data isolation and organization in Liath. Each namespace has its own storage, Lua context, and LuaRocks module tree.

## What are Namespaces?

A namespace is an isolated data container. Think of it like a separate database within Liath:

- Data in one namespace is invisible to queries in another
- Each namespace has its own Lua execution context
- Plugins are initialized separately for each namespace
- LuaRocks modules can be installed per-namespace

## Default Namespace

Every Liath instance has a `default` namespace created automatically:

```python
from liath import EmbeddedLiath

db = EmbeddedLiath(data_dir="./data")

# Operations use the default namespace
db.put("key", "value")  # Stored in 'default' namespace
```

## Creating Namespaces

Create new namespaces for data organization:

```python
# Create namespaces
db.create_namespace("users")
db.create_namespace("products")
db.create_namespace("analytics")

# List all namespaces
namespaces = db.list_namespaces()
print(namespaces)  # ['default', 'users', 'products', 'analytics']
```

## Switching Namespaces

Switch the active namespace to direct operations:

```python
# Switch to users namespace
db.set_namespace("users")

# All operations now use the users namespace
db.put("alice", '{"name": "Alice", "email": "alice@example.com"}')
db.put("bob", '{"name": "Bob", "email": "bob@example.com"}')

# Switch to products namespace
db.set_namespace("products")

# These are stored in products namespace
db.put("laptop", '{"name": "Laptop", "price": 999}')
db.put("phone", '{"name": "Phone", "price": 599}')
```

## Namespace Isolation

Data is completely isolated between namespaces:

```python
# Store in users namespace
db.set_namespace("users")
db.put("count", "2")

# Store in products namespace
db.set_namespace("products")
db.put("count", "10")

# Each namespace has its own value
db.set_namespace("users")
print(db.get("count"))  # Output: 2

db.set_namespace("products")
print(db.get("count"))  # Output: 10
```

## Using the Database Class

For more control, use the `Database` class directly:

```python
from liath import Database

db = Database(data_dir="./data")

# Execute queries in specific namespaces
result = db.execute_query("users", 'return db:get("alice")')
result = db.execute_query("products", 'return db:get("laptop")')
```

## Namespace Use Cases

### Multi-Tenant Applications

```python
# Create namespace per tenant
db.create_namespace("tenant_acme")
db.create_namespace("tenant_globex")

# Each tenant's data is isolated
db.set_namespace("tenant_acme")
db.put("settings", '{"theme": "dark"}')

db.set_namespace("tenant_globex")
db.put("settings", '{"theme": "light"}')
```

### Environment Separation

```python
# Separate environments
db.create_namespace("production")
db.create_namespace("staging")
db.create_namespace("development")
```

### Feature Domains

```python
# Organize by feature
db.create_namespace("auth")      # Authentication data
db.create_namespace("cache")     # Cached data
db.create_namespace("vectors")   # Vector embeddings
```

## Cross-Namespace Operations

While namespaces are isolated, you can access data from multiple namespaces in Python:

```python
def copy_user_to_backup(db, user_id):
    # Read from users namespace
    db.set_namespace("users")
    user_data = db.get(f"user:{user_id}")

    # Write to backup namespace
    db.set_namespace("backup")
    db.put(f"user:{user_id}", user_data)

copy_user_to_backup(db, "123")
```

## Namespace Metadata

Liath stores namespace metadata in `metadata.json`:

```json
{
    "default": {"created": "2024-01-15T10:30:00"},
    "users": {"created": "2024-01-15T10:31:00"},
    "products": {"created": "2024-01-15T10:32:00"}
}
```

## LuaRocks Per Namespace

Each namespace can have its own Lua modules:

```python
from liath import Database

db = Database(data_dir="./data")

# Install a Lua module for specific namespace
db.install_package("analytics", "lua-cjson")
```

## Best Practices

1. **Plan namespace structure**: Design namespaces before building
2. **Use descriptive names**: `users`, `products`, not `ns1`, `ns2`
3. **Don't over-fragment**: Too many namespaces add complexity
4. **Document namespace purposes**: Keep track of what each namespace stores

## Clean Up

```python
db.close()
```

## Next Steps

- [Lua Queries](lua-queries.md) - Write powerful queries
- [Building Plugins](building-plugins.md) - Extend functionality
