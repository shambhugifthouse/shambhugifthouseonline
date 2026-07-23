#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    # Ensure apps directory is in Python path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(base_dir, 'apps'))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shambhu_pos.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
