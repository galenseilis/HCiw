import unittest

from hciw.server_schedules import weekday_server_sched

class TestWeekdayServerSched(unittest.TestCase):

    def test_default_schedule(self):
        result = weekday_server_sched()
        expected = [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [0, 6], [0, 7]]
        self.assertEqual(result, expected)

    def test_offset_schedule(self):
        result = weekday_server_sched(2)
        expected = [[0, 1], [0, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7]]
        self.assertEqual(result, expected)

    def test_negative_offset_schedule(self):
        result = weekday_server_sched(-1)
        expected = [[0, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [0, 7]]
        self.assertEqual(result, expected)

    def test_large_offset_schedule(self):
        result = weekday_server_sched(10)
        expected = [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [0, 6], [0, 7]]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()

