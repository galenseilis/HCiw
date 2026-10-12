import math

import unittest
from unittest.mock import MagicMock

from hciw.waitlist import begin_service_if_possible_accept


class TestBeginServiceIfPossibleAccept(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations
        pass

    def tearDown(self):
        # Clean up any resources created during the test
        pass

    def test_begin_service_if_possible_accept(self):
        # Create mock objects
        node = MagicMock()
        next_individual = MagicMock()

        # Set up the necessary conditions for the test
        node.find_free_server.return_value = MagicMock()
        math.isinf.return_value = False
        node.c = 5  # Set a finite number of servers

        # Call the function to be tested
        begin_service_if_possible_accept(node, next_individual)

        # Assert that the expected methods were called with the expected arguments
        node.find_free_server.assert_called_once_with(next_individual)
        node.decide_preempt.assert_called_once_with(next_individual)
        node.attach_server.assert_called_once_with(
            node.find_free_server.return_value, next_individual
        )
        self.assertEqual(next_individual.service_start_date, 0)
        self.assertEqual(
            next_individual.service_time, node.get_service_time.return_value
        )
        self.assertEqual(next_individual.service_end_date, next_individual.service_time)
        node.next_end_service_date.assert_called_once_with(
            next_individual.service_end_date
        )


if __name__ == "__main__":
    unittest.main()
