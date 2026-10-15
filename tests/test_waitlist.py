import unittest

import hciw
from hciw import waitlist


class TestCreateExistingCustomersFromList(unittest.TestCase):
    def setUp(self):
        self.network = hciw.create_network(
            arrival_distributions=[hciw.dists.Exponential(1.0)],
            service_distributions=[hciw.dists.Exponential(1.0)],
            number_of_servers=[1],
        )
        self.simulation = hciw.Simulation(self.network)
        hciw.seed(1)

    def test_empty_backlog_is_noop(self):
        waitlist.create_existing_customers_from_list([], self.simulation)
        self.assertEqual(self.simulation.nodes[0].number_of_individuals, 0)
        self.assertEqual(self.simulation.nodes[1].number_of_individuals, 0)

    def test_individual_placed_at_node(self):
        waitlist.create_existing_customers_from_list(
            [[1, "Customer", -3.0, 1]], self.simulation
        )
        node = self.simulation.nodes[1]
        self.assertEqual(node.number_of_individuals, 1)
        self.assertEqual(node.all_individuals[0].id_number, 1)

    def test_historical_arrival_date_preserved(self):
        waitlist.create_existing_customers_from_list(
            [[1, "Customer", -5.0, 1]], self.simulation
        )
        self.simulation.simulate_until_max_time(20.0)
        record = self.simulation.get_all_records()[0]
        self.assertEqual(record.arrival_date, -5.0)
        self.assertEqual(record.service_start_date, 0)

    def test_waiting_time_includes_time_before_start(self):
        waitlist.create_existing_customers_from_list(
            [[1, "Customer", -5.0, 1]], self.simulation
        )
        self.simulation.simulate_until_max_time(5)
        record = self.simulation.get_all_records()[0]
        self.assertGreaterEqual(record.waiting_time, 5.0)

    def test_individual_starts_service_immediately_when_server_free(self):
        waitlist.create_existing_customers_from_list(
            [[1, "Customer", -2.0, 1]], self.simulation
        )
        node = self.simulation.nodes[1]
        self.assertEqual(node.number_in_service, 1)
        self.assertEqual(node.number_of_individuals, 1)

    def test_multiple_individuals_queue_when_servers_are_full(self):
        waitlist.create_existing_customers_from_list(
            [
                [1, "Customer", -3.0, 1],
                [2, "Customer", -2.0, 1],
                [3, "Customer", -1.0, 1],
            ],
            self.simulation,
        )
        node = self.simulation.nodes[1]
        self.assertEqual(node.number_in_service, 1)
        self.assertEqual(node.number_of_individuals, 3)

    def test_seeded_identifiers_are_not_reused_by_later_arrivals(self):
        waitlist.create_existing_customers_from_list(
            [
                [1, "Customer", -2.0, 1],
                [2, "Customer", -1.0, 1],
            ],
            self.simulation,
        )
        self.simulation.simulate_until_max_time(5)
        identifiers = [record.id_number for record in self.simulation.get_all_records()]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_advances_arrival_node_counters(self):
        waitlist.create_existing_customers_from_list(
            [[1, "Customer", -2.0, 1]], self.simulation
        )
        arrival_node = self.simulation.nodes[0]
        self.assertEqual(arrival_node.number_of_individuals, 1)
        self.assertEqual(arrival_node.number_accepted_individuals, 1)
        self.assertEqual(arrival_node.number_of_individuals_per_class["Customer"], 1)

    def test_individuals_placed_at_the_requested_nodes(self):
        network = hciw.create_network(
            arrival_distributions=[
                hciw.dists.Exponential(1.0),
                hciw.dists.Exponential(1.0),
            ],
            service_distributions=[
                hciw.dists.Exponential(1.0),
                hciw.dists.Exponential(1.0),
            ],
            number_of_servers=[1, 1],
            routing=[[0.0, 0.0], [0.0, 0.0]],
        )
        simulation = hciw.Simulation(network)
        waitlist.create_existing_customers_from_list(
            [
                [1, "Customer", -2.0, 1],
                [2, "Customer", -2.0, 2],
            ],
            simulation,
        )
        self.assertEqual(simulation.nodes[1].number_of_individuals, 1)
        self.assertEqual(simulation.nodes[2].number_of_individuals, 1)

    def test_customer_class_is_respected(self):
        network = hciw.create_network(
            arrival_distributions={"Class 0": [hciw.dists.Exponential(1.0)]},
            service_distributions={"Class 0": [hciw.dists.Exponential(1.0)]},
            number_of_servers=[1],
        )
        simulation = hciw.Simulation(network)
        waitlist.create_existing_customers_from_list(
            [[1, "Class 0", -2.0, 1]], simulation
        )
        simulation.simulate_until_max_time(5)
        record = simulation.get_all_records()[0]
        self.assertEqual(record.customer_class, "Class 0")


class TestAccept(unittest.TestCase):
    def test_accept_places_an_individual(self):
        network = hciw.create_network(
            arrival_distributions=[hciw.dists.Exponential(1.0)],
            service_distributions=[hciw.dists.Exponential(1.0)],
            number_of_servers=[1],
        )
        simulation = hciw.Simulation(network)
        node = simulation.nodes[1]
        waitlist.accept(42, "Customer", -4.0, node, simulation)
        self.assertEqual(node.number_of_individuals, 1)
        individual = node.all_individuals[0]
        self.assertEqual(individual.id_number, 42)
        self.assertEqual(individual.arrival_date, -4.0)
        self.assertEqual(individual.service_start_date, 0)

    def test_accept_resets_the_current_time_to_the_start(self):
        network = hciw.create_network(
            arrival_distributions=[hciw.dists.Exponential(1.0)],
            service_distributions=[hciw.dists.Exponential(1.0)],
            number_of_servers=[1],
        )
        simulation = hciw.Simulation(network)
        simulation.current_time = 10.0
        waitlist.accept(1, "Customer", -4.0, simulation.nodes[1], simulation)
        self.assertEqual(simulation.current_time, 0)


if __name__ == "__main__":
    unittest.main()
