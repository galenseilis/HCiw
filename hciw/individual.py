"""The individual agent that flows through a queueing network."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hciw.server import Server


class Individual:
    """Represent an individual agent in a queueing network simulation.

    An ``Individual`` models the flow of an agent through a queueing
    network, tracking its arrival time, service time, priority and other
    relevant data.

    Attributes:
        arrival_date (bool or float): Timestamp of the individual's arrival.
        service_start_date (bool or float): Timestamp the current service
            started.
        service_time (bool or float): Duration of the current service.
        service_end_date (bool or float): Timestamp the current service ends.
        exit_date (bool or float): Timestamp the individual exits the system.
        id_number (int): Unique identifier for the individual.
        data_records (list): The data records attached to the individual.
        customer_class (str): The customer class of the individual.
        previous_class (str): The previous customer class of the individual.
        priority_class (int): The priority class of the individual.
        prev_priority_class (int): The previous priority class of the
            individual.
        original_class (str): The original customer class of the individual.
        is_blocked (bool): Whether the individual is blocked.
        server (bool or Server): The server assigned to the individual, if any.
        queue_size_at_arrival (bool or int): Queue size when the individual
            arrived.
        queue_size_at_departure (bool or int): Queue size when the individual
            departed.
        destination (bool or int): The destination node in the network.
        interrupted (bool): Whether the individual's service was interrupted.
        node (bool or int): The node where the individual is located.
        simulation (bool or Simulation): The simulation the individual belongs
            to.

    Example:
        .. code-block:: python

            individual = Individual(
                id_number=1, customer_class='Gold', priority_class=1,
                simulation=True,
            )
    """

    def __init__(
        self, id_number, customer_class="Customer", priority_class=0, simulation=False
    ):
        """Initialise an ``Individual``.

        Args:
            id_number (int): A unique identifier for the individual.
            customer_class (str, optional): The customer class the individual
                belongs to. Defaults to ``'Customer'``.
            priority_class (int, optional): The priority class of the
                individual. Defaults to ``0``.
            simulation (bool or Simulation, optional): The simulation the
                individual is part of. Defaults to ``False``.
        """
        self.arrival_date = False
        self.service_start_date = False
        self.service_time: float | bool | str = False
        self.service_end_date = False
        self.exit_date = False
        self.id_number = id_number
        self.data_records = []
        self.customer_class = customer_class
        self.previous_class = customer_class
        self.priority_class = priority_class
        self.prev_priority_class = priority_class
        self.original_class = customer_class
        self.is_blocked = False
        self.server: Server | bool = False
        self.queue_size_at_arrival: int | bool = False
        self.queue_size_at_departure: int | bool = False
        self.destination: int | bool = False
        self.interrupted = False
        self.node = False
        self.simulation = simulation

    next_class: str
    class_change_date: float | bool
    reneging_date: float | bool
    starting_node: int
    original_service_start_date: float | bool
    original_service_time: float | bool | str
    time_left: float | bool
    route: list
    with_server: bool
    date_last_update: float | bool

    def __repr__(self) -> str:
        """Return a string representation of the individual.

        Returns:
            str: The individual represented as ``'Individual <id_number>'``.
        """
        return f"Individual {self.id_number}"
