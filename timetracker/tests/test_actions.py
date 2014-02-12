import unittest
import os

from timetracker.timetracker import TimeTracker


class TestActions(unittest.TestCase):
		def setUp(self):
			pass

		def tearDown(self):
			os.remove('test.db')

		def test_db_creation(self):
			tt = TimeTracker(database_path='test.db', project='test')
			self.assertTrue(os.path.exists('test.db'))