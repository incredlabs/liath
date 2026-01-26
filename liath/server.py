"""
HTTP REST API server for Liath database.

This module provides a Flask-based HTTP server with endpoints for
authentication, namespace management, and query execution.
"""

from flask import Flask, request, jsonify
from .database import Database
import threading
from concurrent.futures import ThreadPoolExecutor
import json
import argparse

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=20)


def create_app(storage_type='auto', data_dir='./data', plugins_dir=None):
    """Create and configure the Flask application.

    Args:
        storage_type: Storage backend ('auto', 'rocksdb', 'leveldb').
        data_dir: Path to the data directory.
        plugins_dir: Optional path to custom plugins directory.

    Returns:
        Configured Flask application instance.
    """
    db = Database(storage_type=storage_type, data_dir=data_dir, plugins_dir=plugins_dir)
    app.config['db'] = db
    return app


def execute_query(namespace, query):
    """Execute a Lua query and return JSON result.

    Internal helper function used by the /query endpoint.

    Args:
        namespace: The namespace to execute the query in.
        query: Lua code to execute.

    Returns:
        JSON string with the query result or error message.
    """
    db = app.config['db']
    try:
        result = db.execute_query(namespace, query)
        if isinstance(result, (dict, list)):
            return json.dumps(result)
        elif isinstance(result, str):
            return result
        else:
            return json.dumps({"result": str(result)})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@app.route('/login', methods=['POST'])
def login():
    """Authenticate a user.

    POST /login
    Body: {"username": "...", "password": "..."}

    Returns:
        JSON with status "success" or "error".
    """
    data = request.json
    db = app.config['db']
    if db.authenticate_user(data['username'], data['password']):
        return jsonify({"status": "success", "message": "Logged in successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/create_user', methods=['POST'])
def create_user():
    """Create a new user account.

    POST /create_user
    Body: {"username": "...", "password": "..."}

    Returns:
        JSON with status "success" or "error".
    """
    data = request.json
    db = app.config['db']
    try:
        db.create_user(data['username'], data['password'])
        return jsonify({"status": "success", "message": "User created successfully"})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/query', methods=['POST'])
def query():
    """Execute a Lua query.

    POST /query
    Body: {"namespace": "...", "query": "..."}

    Returns:
        JSON with query result or error.
    """
    data = request.json
    future = executor.submit(execute_query, data['namespace'], data['query'])
    result = future.result()
    return result, 200, {'Content-Type': 'application/json'}

@app.route('/create_namespace', methods=['POST'])
def create_namespace():
    """Create a new namespace.

    POST /create_namespace
    Body: {"namespace": "..."}

    Returns:
        JSON with status "success".
    """
    data = request.json
    db = app.config['db']
    db.create_namespace(data['namespace'])
    return jsonify({"status": "success", "message": f"Namespace {data['namespace']} created"})

@app.route('/list_namespaces', methods=['GET'])
def list_namespaces():
    """List all available namespaces.

    GET /list_namespaces

    Returns:
        JSON with status and list of namespace names.
    """
    db = app.config['db']
    return jsonify({"status": "success", "namespaces": db.list_namespaces()})


def run_server(host='0.0.0.0', port=5000):
    """Start the HTTP server.

    Args:
        host: Host address to bind to. Defaults to '0.0.0.0'.
        port: Port number to listen on. Defaults to 5000.
    """
    app.run(host=host, port=port, threaded=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Liath Database Server")
    parser.add_argument('--storage', choices=['auto', 'rocksdb', 'leveldb'], default='auto',
                        help="Specify the storage backend to use")
    parser.add_argument('--data-dir', default='./data', help="Specify the data directory")
    parser.add_argument('--plugins-dir', default=None, help="Specify an additional plugins directory")
    parser.add_argument('--host', default='0.0.0.0', help="Specify the host to run the server on")
    parser.add_argument('--port', type=int, default=5000, help="Specify the port to run the server on")
    args = parser.parse_args()

    app = create_app(storage_type=args.storage, data_dir=args.data_dir, plugins_dir=args.plugins_dir)
    server_thread = threading.Thread(target=run_server, args=(args.host, args.port))
    server_thread.start()
    print(f"Server is running on http://{args.host}:{args.port}")
    server_thread.join()
