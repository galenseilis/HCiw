"""Exit node of the queueing network."""


class ExitNode:
    """Represent the exit node of the network."""

    def __init__(self):
        """Initialise the exit node."""
        self.all_individuals = []
        self.number_of_individuals = 0
        self.number_of_completed_individuals = 0
        self.id_number = -1
        self.next_event_date = float("Inf")
        self.node_capacity = float("Inf")

    def __repr__(self):
        """Return a string representation of the exit node.

        Returns:
            str: The representation of the exit node.
        """
        return "Exit Node"

    def accept(self, next_individual, completed=True):
        """Add an individual to the list of completed individuals.

        Args:
            next_individual (Individual): The individual to accept.
            completed (bool): Whether the individual completed service.
        """
        self.all_individuals.append(next_individual)
        next_individual.node = -1
        self.number_of_individuals += 1
        if completed:
            self.number_of_completed_individuals += 1

    def update_next_event_date(self):
        """Do nothing, as the next event date is always the max time."""
        pass
