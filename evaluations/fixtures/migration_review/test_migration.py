from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parent


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.addCleanup(self.connection.close)
        self.connection.executescript((ROOT / 'schema.sql').read_text())

    def candidate(self):
        self.connection.execute((ROOT / 'candidate.sql').read_text())

    def test_unsafe_migration_fails_on_existing_records(self):
        with self.assertRaises(sqlite3.OperationalError) as error:
            self.connection.execute((ROOT / 'unsafe.sql').read_text())
        self.assertIn('NOT NULL', str(error.exception))
        self.assertEqual([row[1] for row in self.connection.execute('PRAGMA table_info(orders)')], ['id', 'total_cents'])
        self.assertEqual(self.connection.execute('SELECT * FROM orders').fetchall(), [('A1', 2500)])

    def test_candidate_preserves_and_backfills_existing_records(self):
        self.candidate()
        self.assertEqual(self.connection.execute('SELECT * FROM orders').fetchall(), [('A1', 2500, 'pending')])

    def test_new_insert_uses_default(self):
        self.candidate()
        self.connection.execute("INSERT INTO orders (id, total_cents) VALUES ('A2', 100)")
        self.assertEqual(self.connection.execute("SELECT status FROM orders WHERE id='A2'").fetchone(), ('pending',))

    def test_null_status_is_rejected(self):
        self.candidate()
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute("INSERT INTO orders VALUES ('A2', 100, NULL)")

    def test_candidate_ddl_rolls_back_in_explicit_transaction(self):
        self.connection.execute('BEGIN')
        self.candidate()
        self.connection.rollback()
        self.assertEqual([row[1] for row in self.connection.execute('PRAGMA table_info(orders)')], ['id', 'total_cents'])
        self.assertEqual(self.connection.execute('SELECT * FROM orders').fetchall(), [('A1', 2500)])
