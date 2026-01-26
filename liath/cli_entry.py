#!/usr/bin/env python3
"""
Liath CLI entry point.

This module provides a command-line interface for interacting with the Liath database.
"""

import argparse
import sys

from liath import DatabaseCLI


def main():
    """Main entry point for the Liath CLI."""
    parser = argparse.ArgumentParser(description="Liath Database CLI")
    parser.add_argument('--storage', choices=['auto', 'rocksdb', 'leveldb'], default='auto',
                        help="Specify the storage backend to use")
    parser.add_argument('--data-dir', default='./data',
                        help="Specify the data directory")
    parser.add_argument('--plugins-dir', default=None,
                        help="Specify an additional plugins directory")
    
    args = parser.parse_args()
    
    try:
        cli = DatabaseCLI(storage_type=args.storage, data_dir=args.data_dir, plugins_dir=args.plugins_dir)
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
