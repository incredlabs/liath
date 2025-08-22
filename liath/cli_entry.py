#!/usr/bin/env python3
"""
Liath CLI entry point.

This module provides a command-line interface for interacting with the Liath database.
"""

import argparse
import sys
import os

# Add the parent directory to the path so we can import liath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from liath import DatabaseCLI


def main():
    """Main entry point for the Liath CLI."""
    parser = argparse.ArgumentParser(description="Liath Database CLI")
    parser.add_argument('--storage', choices=['auto', 'rocksdb', 'leveldb'], default='auto',
                        help="Specify the storage backend to use")
    parser.add_argument('--data-dir', default='./data',
                        help="Specify the data directory")
    parser.add_argument('--plugins-dir', default='./plugins',
                        help="Specify the plugins directory")
    
    args = parser.parse_args()
    
    try:
        cli = DatabaseCLI(storage_type=args.storage)
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()