import unittest
from decimal import Decimal

import hciw


def two_class_network(discipline, benchmarks):
    """A one-server network where the benchmark changes the service order."""
    return hciw.create_network(
        arrival_distributions={
            "Blue": [hciw.dists.Sequential([1.0, 1.0, 1000.0])],
            "Red": [hciw.dists.Sequential([3.0, 1000.0])],
        },
        service_distributions={
            "Blue": [hciw.dists.Deterministic(5.0)],
            "Red": [hciw.dists.Deterministic(5.0)],
        },
        number_of_servers=[1],
        service_disciplines=[discipline],
        customer_class_benchmarks=benchmarks,
    )


class TestWaitTimeOverBenchmark(unittest.TestCase):
    def test_serves_class_furthest_over_its_benchmark(self):
        # Blue has a large benchmark (10) and Red a strict one (0). At time 6
        # Blue #2 (arrived 2, so 4 over its benchmark of 10 is -6 under) and
        # Red #1 (arrived 3, so 3 over its benchmark of 0) are both waiting;
        # Red is furthest over and is served next, ahead of the earlier Blue.
        N = two_class_network(
            hciw.disciplines.wait_time_over_benchmark,
            {"Blue": 10.0, "Red": 0.0},
        )
        Q = hciw.Simulation(N)
        Q.simulate_until_max_time(17.0)
        recs = sorted(Q.get_all_records(), key=lambda r: r.service_start_date)
        self.assertEqual(
            [(r.id_number, r.customer_class, r.service_start_date) for r in recs],
            [(1, "Blue", 1.0), (3, "Red", 6.0), (2, "Blue", 11.0)],
        )

    def test_differs_from_fifo(self):
        # The same network with FIFO serves the earlier Blue #2 ahead of Red.
        N = two_class_network(
            hciw.disciplines.FIFO,
            {"Blue": 10.0, "Red": 0.0},
        )
        Q = hciw.Simulation(N)
        Q.simulate_until_max_time(17.0)
        recs = sorted(Q.get_all_records(), key=lambda r: r.service_start_date)
        self.assertEqual(
            [(r.id_number, r.customer_class) for r in recs],
            [(1, "Blue"), (2, "Blue"), (3, "Red")],
        )

    def test_exact_arithmetic(self):
        N = two_class_network(
            hciw.disciplines.wait_time_over_benchmark,
            {"Blue": 10.0, "Red": 0.0},
        )
        Q = hciw.Simulation(N, exact=26)
        Q.simulate_until_max_time(17.0)
        recs = sorted(Q.get_all_records(), key=lambda r: r.service_start_date)
        self.assertEqual(
            [r.service_start_date for r in recs],
            [Decimal("1.0"), Decimal("6.0"), Decimal("11.0")],
        )

    def test_benchmarks_stored_on_customer_classes(self):
        N = two_class_network(
            hciw.disciplines.wait_time_over_benchmark,
            {"Blue": 10.0, "Red": 0.0},
        )
        self.assertEqual(N.customer_classes["Blue"].benchmark, 10.0)
        self.assertEqual(N.customer_classes["Red"].benchmark, 0.0)

    def test_missing_benchmark_raises(self):
        N = hciw.create_network(
            arrival_distributions=[hciw.dists.Deterministic(1.0)],
            service_distributions=[hciw.dists.Deterministic(3.0)],
            number_of_servers=[1],
            service_disciplines=[hciw.disciplines.wait_time_over_benchmark],
        )
        self.assertIsNone(N.customer_classes["Customer"].benchmark)
        Q = hciw.Simulation(N)
        with self.assertRaises(ValueError):
            Q.simulate_until_max_time(10.0)


class TestBenchmarkValidation(unittest.TestCase):
    def test_non_dictionary_benchmarks(self):
        with self.assertRaises(ValueError):
            hciw.create_network(
                arrival_distributions=[hciw.dists.Deterministic(1.0)],
                service_distributions=[hciw.dists.Deterministic(1.0)],
                number_of_servers=[1],
                customer_class_benchmarks=[1.0],
            )

    def test_unknown_class_name(self):
        with self.assertRaises(ValueError):
            hciw.create_network(
                arrival_distributions=[hciw.dists.Deterministic(1.0)],
                service_distributions=[hciw.dists.Deterministic(1.0)],
                number_of_servers=[1],
                customer_class_benchmarks={"Nope": 1.0},
            )

    def test_non_numeric_benchmark(self):
        with self.assertRaises(ValueError):
            hciw.create_network(
                arrival_distributions=[hciw.dists.Deterministic(1.0)],
                service_distributions=[hciw.dists.Deterministic(1.0)],
                number_of_servers=[1],
                customer_class_benchmarks={"Customer": "soon"},
            )

    def test_boolean_benchmark(self):
        with self.assertRaises(ValueError):
            hciw.create_network(
                arrival_distributions=[hciw.dists.Deterministic(1.0)],
                service_distributions=[hciw.dists.Deterministic(1.0)],
                number_of_servers=[1],
                customer_class_benchmarks={"Customer": True},
            )

    def test_none_benchmark_allowed(self):
        N = hciw.create_network(
            arrival_distributions=[hciw.dists.Deterministic(1.0)],
            service_distributions=[hciw.dists.Deterministic(1.0)],
            number_of_servers=[1],
            customer_class_benchmarks={"Customer": None},
        )
        self.assertIsNone(N.customer_classes["Customer"].benchmark)
