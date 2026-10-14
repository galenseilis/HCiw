"""Arrival node of the queueing network."""

from random import random


class ArrivalNode:
    """Represent the arrival node of the network.

    This class handles arrivals, baulking, and rejections of individuals.
    See `hciw.Simulation` for the main simulation class.
    """

    def __init__(self, simulation):
        """Initialise the arrival node.

        Args:
            simulation (object): The simulation to which this arrival node
                belongs.
        """
        self.simulation = simulation
        self.number_of_individuals = 0
        self.all_individuals = []
        self.number_of_individuals_per_class = {
            clss: 0 for clss in self.simulation.network.customer_class_names
        }
        self.number_accepted_individuals = 0
        self.number_accepted_individuals_per_class = {
            clss: 0 for clss in self.simulation.network.customer_class_names
        }
        self.system_capacity = self.simulation.network.system_capacity
        self.event_dates_dict: dict[int, dict[str, float | bool]] = {
            nd + 1: {
                clss: False for clss in self.simulation.network.customer_class_names
            }
            for nd in range(self.simulation.network.number_of_nodes)
        }

    def initialise(self):
        """Initialise the event dates dictionary and next event date."""
        self.initialise_event_dates_dict()
        self.find_next_event_date()

    def __repr__(self):
        """Return a string representation of the arrival node.

        Returns:
            str: The representation of the arrival node.
        """
        return "Arrival Node"

    def decide_baulk(self, next_node, next_individual):
        """Either make an individual baulk or send them to the next node.

        Args:
            next_node (Node): The next node.
            next_individual (Individual): The individual being considered.
        """
        if next_node.baulking_functions[self.next_class] is None:
            self.send_individual(next_node, next_individual)
        else:
            rnd_num = random()
            if rnd_num < next_node.baulking_functions[self.next_class](
                next_node.number_of_individuals,
                Q=self.simulation,
                next_ind=next_individual,
                next_node=next_node,
            ):
                self.record_baulk(next_node, next_individual)
                self.simulation.nodes[-1].accept(next_individual, completed=False)
            else:
                self.send_individual(next_node, next_individual)

    def find_next_event_date(self):
        """Find the time of the next arrival."""
        minnd = None
        minclss = None
        mindate = float("Inf")
        for nd in self.event_dates_dict:
            for clss in self.event_dates_dict[nd]:
                if self.event_dates_dict[nd][clss] < mindate:
                    minnd = nd
                    minclss = clss
                    mindate = self.event_dates_dict[nd][clss]
        self.next_node = minnd
        self.next_class = minclss
        self.next_event_date = mindate

    def have_event(self):
        """Create and send a batch of arriving individuals.

        Finds a batch size, creates that many individuals, sends them to the
        relevant node, then updates the event dates dictionary.
        """
        batch = self.batch_size(self.next_node, self.next_class)
        assert self.next_node is not None
        assert self.next_class is not None
        for _ in range(batch):
            self.number_of_individuals += 1
            self.number_of_individuals_per_class[self.next_class] += 1
            priority_class = self.simulation.network.priority_class_mapping[
                self.next_class
            ]
            next_individual = self.simulation.IndividualType(
                self.number_of_individuals,
                self.next_class,
                priority_class,
                simulation=self.simulation,
            )
            next_node = self.simulation.transitive_nodes[self.next_node - 1]
            next_individual.starting_node = next_node.id_number
            self.simulation.routers[
                next_individual.customer_class
            ].initialise_individual(next_individual)
            self.release_individual(next_node, next_individual)

        self.event_dates_dict[self.next_node][self.next_class] = self.increment_time(
            self.event_dates_dict[self.next_node][self.next_class],
            self.inter_arrival(self.next_node, self.next_class),
        )
        self.find_next_event_date()

    def increment_time(self, original, increment):
        """Increment the original time by the increment.

        Args:
            original (float): The original time.
            increment (float): The amount to add.

        Returns:
            The incremented time.
        """
        return original + increment

    def initialise_event_dates_dict(self):
        """Initialise the event dates dictionary.

        Random times are sampled for each node and class.
        """
        for nd in self.event_dates_dict:
            for clss in self.event_dates_dict[nd]:
                if self.simulation.inter_arrival_times[nd][clss] is not None:
                    self.event_dates_dict[nd][clss] = self.inter_arrival(nd, clss)
                else:
                    self.event_dates_dict[nd][clss] = float("inf")

    def inter_arrival(self, nd, clss):
        """Sample the inter-arrival time for the next class and node.

        Args:
            nd (int): The destination node.
            clss (str): The customer class.

        Returns:
            The sampled inter-arrival time.
        """
        return self.simulation.inter_arrival_times[nd][clss]._sample(
            t=self.simulation.current_time
        )

    def batch_size(self, nd, clss):
        """Sample the batch size for the next class and node.

        Args:
            nd (int): The destination node.
            clss (str): The customer class.

        Returns:
            int: The sampled batch size.

        Raises:
            ValueError: If the sampled batch size is not a non-negative
                integer.
        """
        batch = self.simulation.batch_sizes[nd][clss]._sample(
            t=self.simulation.current_time
        )
        if isinstance(batch, int) and batch >= 0:
            return batch
        raise ValueError("Batch sizes must be positive integers.")

    def record_baulk(self, next_node, individual):
        """Write a baulking record for an individual.

        Args:
            next_node (Node): The node the individual would have joined.
            individual (Individual): The baulking individual.
        """
        next_node.write_baulking_or_rejection_record(individual, record_type="baulk")

    def record_rejection(self, next_node, individual):
        """Write a rejection record for an individual.

        Args:
            next_node (Node): The node the individual was rejected from.
            individual (Individual): The rejected individual.
        """
        next_node.write_baulking_or_rejection_record(
            individual, record_type="rejection"
        )

    def release_individual(self, next_node, next_individual):
        """Release an individual to the next node.

        Either rejects the individual due to lack of capacity, or sends that
        individual to baulk or not.

        Args:
            next_node (Node): The next node.
            next_individual (Individual): The individual being released.
        """
        if (next_node.number_of_individuals >= next_node.node_capacity) or (
            self.simulation.number_of_individuals >= self.system_capacity
        ):
            self.record_rejection(next_node, next_individual)
            self.simulation.nodes[-1].accept(next_individual, completed=False)
        else:
            self.decide_baulk(next_node, next_individual)

    def send_individual(self, next_node, next_individual):
        """Send the next individual to the next node.

        Args:
            next_node (Node): The next node.
            next_individual (Individual): The individual being sent.
        """
        self.number_accepted_individuals += 1
        self.number_accepted_individuals_per_class[next_individual.customer_class] += 1
        next_node.accept(next_individual)

    def update_next_event_date(self):
        """Do nothing, as the next event update happens at the event time."""
        pass
