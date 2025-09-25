import os
import sys


# Ensure project root is on sys.path for 'app' imports when running pytest
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


