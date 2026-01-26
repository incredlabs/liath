# HTTP API Reference

Liath provides a REST API for remote database access.

## Starting the Server

```bash
liath-server [OPTIONS]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Server bind address |
| `--port` | `5000` | Server port |
| `--data-dir` | `./data` | Data directory path |
| `--storage` | `auto` | Storage backend: `auto`, `rocksdb`, `leveldb` |
| `--help` | - | Show help message |

### Examples

```bash
# Default configuration
liath-server

# Custom host and port
liath-server --host 127.0.0.1 --port 8080

# Production configuration
liath-server --host 0.0.0.0 --port 5000 --data-dir /var/lib/liath --storage rocksdb
```

## Authentication

Currently, the API uses username/password authentication. Include credentials in requests where noted.

## Endpoints

### POST /login

Authenticate a user.

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "Logged in"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Invalid credentials"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}'
```

### POST /create_user

Create a new user.

**Request:**
```json
{
    "username": "newuser",
    "password": "password123"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "User created"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "User already exists"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/create_user \
    -H "Content-Type: application/json" \
    -d '{"username": "alice", "password": "securepass"}'
```

### POST /query

Execute a Lua query.

**Request:**
```json
{
    "namespace": "default",
    "query": "return db:get(\"key\")"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "result": "value"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Query execution failed: ..."
}
```

**Examples:**

Simple get:
```bash
curl -X POST http://localhost:5000/query \
    -H "Content-Type: application/json" \
    -d '{"namespace": "default", "query": "return db:get(\"name\")"}'
```

Put operation:
```bash
curl -X POST http://localhost:5000/query \
    -H "Content-Type: application/json" \
    -d '{"namespace": "default", "query": "db:put(\"name\", \"Alice\"); return \"ok\""}'
```

Complex query:
```bash
curl -X POST http://localhost:5000/query \
    -H "Content-Type: application/json" \
    -d '{
        "namespace": "default",
        "query": "local items = db:iterator(); local count = 0; for _ in pairs(items) do count = count + 1 end; return count"
    }'
```

### POST /create_namespace

Create a new namespace.

**Request:**
```json
{
    "name": "users"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "Namespace created"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Namespace already exists"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/create_namespace \
    -H "Content-Type: application/json" \
    -d '{"name": "products"}'
```

### GET /list_namespaces

List all available namespaces.

**Response:**
```json
{
    "status": "success",
    "namespaces": ["default", "users", "products"]
}
```

**Example:**
```bash
curl http://localhost:5000/list_namespaces
```

## Error Responses

All endpoints return errors in this format:

```json
{
    "status": "error",
    "message": "Description of the error"
}
```

HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid JSON, missing fields) |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Internal server error |

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:5000"

class LiathClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        return response.json()

    def query(self, namespace, lua_query):
        response = requests.post(
            f"{self.base_url}/query",
            json={"namespace": namespace, "query": lua_query}
        )
        return response.json()

    def create_namespace(self, name):
        response = requests.post(
            f"{self.base_url}/create_namespace",
            json={"name": name}
        )
        return response.json()

    def list_namespaces(self):
        response = requests.get(f"{self.base_url}/list_namespaces")
        return response.json()

# Usage
client = LiathClient("http://localhost:5000")
client.login("admin", "admin123")
result = client.query("default", 'return db:get("key")')
print(result)
```

## JavaScript/Node.js Example

```javascript
const BASE_URL = 'http://localhost:5000';

async function query(namespace, luaQuery) {
    const response = await fetch(`${BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ namespace, query: luaQuery })
    });
    return response.json();
}

// Usage
const result = await query('default', 'return db:get("key")');
console.log(result);
```

## cURL Examples

### Complete Workflow

```bash
# 1. Create a user
curl -X POST http://localhost:5000/create_user \
    -H "Content-Type: application/json" \
    -d '{"username": "demo", "password": "demo123"}'

# 2. Login
curl -X POST http://localhost:5000/login \
    -H "Content-Type: application/json" \
    -d '{"username": "demo", "password": "demo123"}'

# 3. Create a namespace
curl -X POST http://localhost:5000/create_namespace \
    -H "Content-Type: application/json" \
    -d '{"name": "myapp"}'

# 4. Store data
curl -X POST http://localhost:5000/query \
    -H "Content-Type: application/json" \
    -d '{"namespace": "myapp", "query": "db:put(\"config\", \"{\\\"version\\\": 1}\")"}'

# 5. Retrieve data
curl -X POST http://localhost:5000/query \
    -H "Content-Type: application/json" \
    -d '{"namespace": "myapp", "query": "return db:get(\"config\")"}'

# 6. List namespaces
curl http://localhost:5000/list_namespaces
```

## Security Considerations

1. **Use HTTPS in production**: Run behind a reverse proxy with TLS
2. **Strong passwords**: Enforce strong password policies
3. **Network isolation**: Restrict access to trusted networks
4. **Input validation**: The server validates input, but add application-level checks
