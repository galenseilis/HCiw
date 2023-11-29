from dataclasses import dataclass
import unittest

import hciw
import numpy as np

class TestWaitTimeOverBenchmark(unittest.TestCase):
    def setUp(self):

        @dataclass(order=True, frozen=True)
        class MockBenchmarkClass:
            benchmark: float

        @dataclass()
        class MockIndividual:
            customer_class: type
            arrival_date: float
        
        self.mock_benchmark_class = MockBenchmarkClass
        self.mock_individual_class = MockIndividual

    def test_wait_time_over_benchmark(self):
        # Test when the list is empty, it should return None
        self.assertIsNone(wait_time_over_benchmark([]))

        # Test when there is only one individual, it should return that individual
        ind1 = self.mock_individual_class(self.mock_benchmark_class(10), 5)
        self.assertEqual(hciw.wait_time_over_benchmark([ind1]), ind1)

        # Test when the benchmark differences are the same for all individuals, it should return the first one
        ind2 = self.mock_individual_class(self.mock_benchmark_class(15), 7)
        ind3 = self.mock_individual_class(self.mock_benchmark_class(12), 3)
        self.assertEqual(hciw.wait_time_over_benchmark([ind1, ind2, ind3]), ind1)

        # Test when the benchmark differences are different, it should return the one with the highest difference
        ind4 = self.mock_individual_class(self.mock_benchmark_class(18), 9)
        self.assertEqual(hciw.wait_time_over_benchmark([ind1, ind2, ind3, ind4]), ind4)

        # Test when the benchmark differences are negative, it should return the one with the highest negative difference
        ind5 = self.mock_individual_class(self.mock_benchmark_class(8), 2)
        self.assertEqual(hciw.wait_time_over_benchmark([ind1, ind2, ind3, ind4, ind5]), ind5)

if __name__ == '__main__':
    unittest.main()
