# Quick Start

Get started with Liath in 5 minutes. This guide shows the basics of using Liath as a Python library.

## Setup

First, install Liath:

```bash
pip install liath
```

## Basic Usage

### Initialize the Database

```python
from liath import EmbeddedLiath

# Create a database instance
db = EmbeddedLiath(data_dir="./my_data")
```

The `data_dir` parameter specifies where Liath stores its data files.

### Store and Retrieve Data

```python
# Store a value
db.put("user:1:name", "Alice")
db.put("user:1:email", "alice@example.com")

# Retrieve values
name = db.get("user:1:name")
print(name)  # Output: Alice

# Delete a value
db.delete("user:1:email")
```

### Execute Lua Queries

Liath uses Lua as its query language for complex operations:

```python
# Simple query
result = db.execute_lua('return db:get("user:1:name")')
print(result)  # Output: Alice

# Query with logic
result = db.execute_lua('''
    local name = db:get("user:1:name")
    if name then
        return "Found user: " .. name
    else
        return "User not found"
    end
''')
print(result)  # Output: Found user: Alice
```

### Work with Namespaces

Namespaces isolate data and provide separate contexts:

```python
# Create a namespace
db.create_namespace("users")

# Switch to the namespace
db.set_namespace("users")

# Data is now stored in the "users" namespace
db.put("alice", '{"name": "Alice", "role": "admin"}')

# List all namespaces
namespaces = db.list_namespaces()
print(namespaces)  # Output: ['default', 'users']
```

### Clean Up

Always close the database when done:

```python
db.close()
```

## Using the CLI

Liath also provides a command-line interface:

```bash
# Start the CLI
liath-cli --data-dir ./my_data

# In the CLI:
> login admin admin123
> use default
> query return db:get("user:1:name")
```

## Using the HTTP API

Start the HTTP server:

```bash
liath-server --host 0.0.0.0 --port 5000 --data-dir ./my_data
```

Make requests:

```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Execute a query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"namespace": "default", "query": "return db:get(\"user:1:name\")"}'
```

## Next Steps

- [Configuration Guide](configuration.md) - Learn about storage backends and options
- [Basic Operations Tutorial](../tutorials/basic-operations.md) - Deeper dive into CRUD operations
- [Lua Queries Tutorial](../tutorials/lua-queries.md) - Master the query language
- [Vector Search Tutorial](../tutorials/vector-search.md) - Build RAG applications
