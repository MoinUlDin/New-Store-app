# tests/conftest.py
import sys
import os
import pytest
import tempfile

# --- Ensure project root is on sys.path so tests can import local packages like `data`, `services`, etc. ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))       # .../tests
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))   # project root
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from data import db as data_db


@pytest.fixture(scope="function")
def test_db(tmp_path):
    """Create a temporary DB for each test and bootstrap schema.
    Returns a sqlite3.Connection instance.
    """
    db_file = tmp_path / "kiryana.sqlite"
    db_path = str(db_file)

    # point module-level DB_PATH to our temp file for other callers
    data_db.DB_PATH = db_path

    # bootstrap (no migrations)
    # IMPORTANT: bootstrap() returns a connection that we must close to avoid long-lived writer locking.
    conn_boot = data_db.bootstrap(db_path=db_path, migrations_dir=None, ensure_accounts={
        'superadmin_email': 'moinuldinc@gmail.com',
        'superadmin_password': 'Abnsbghh.147',
        'shopkeeper_username': 'admin',
        'shopkeeper_password': 'admin'
    })
    # close bootstrap connection to avoid lock contention
    try:
        conn_boot.close()
    except Exception:
        pass

    # open a fresh connection to return to the test
    conn = data_db.get_connection(db_path)

    yield conn

    try:
        conn.close()
    except Exception:
        pass
