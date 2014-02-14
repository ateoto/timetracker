import unittest
import os

from timetracker.timetracker import TimeTracker


class TestActions(unittest.TestCase):
		def setUp(self):
			self.tt = TimeTracker(database_path=':memory:', project='test')

		def tearDown(self):
			pass

		@unittest.skip
		def test_db_creation(self):
			self.assertTrue(os.path.exists('test.db'))

		def test_get_active_tests_no_tasks(self):
			tasks = self.tt._get_active_tasks()
			self.assertEqual(len(tasks), 0)

		def test_add_task(self):
			self.tt.start('test task')
			tasks = self.tt._get_active_tasks()
			self.assertIn('test task', [task.name for task in tasks])