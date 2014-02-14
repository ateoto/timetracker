import unittest
import sys

from timetracker.timetracker import TimeTracker


class TestActions(unittest.TestCase):
        def setUp(self):
            self.tt = TimeTracker(database_path=':memory:', project='test')

        def tearDown(self):
            pass

        def test_get_active_tests_no_tasks(self):
            tasks = self.tt._get_active_tasks()
            self.assertEqual(len(tasks), 0)

        def test_add_task(self):
            self.tt.start('test task')
            if not hasattr(sys.stdout, "getvalue"):
                self.fail("Please run in Buffer mode '--buffer'")
            
            output = sys.stdout.getvalue().strip()
            self.assertEqual(output, 'Started test task')
            tasks = self.tt._get_active_tasks()
            self.assertIn('test task', [task.name for task in tasks])

        def test_stop_task(self):
            self.tt.start('test task')
            self.tt.stop()
            if not hasattr(sys.stdout, "getvalue"):
                self.fail("Please run in Buffer mode '--buffer'")

            output = sys.stdout.getvalue().strip().split('\n')[1]
            self.assertEqual(output, 'test task completed in 0 minutes')
            tasks = self.tt._get_active_tasks()
            self.assertEqual(len(tasks), 0)