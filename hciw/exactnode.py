"""Node classes with exact numerical precision."""

from decimal import Decimal

from .arrival_node import ArrivalNode
from .node import Node
from .server import Server


class ExactNode(Node):
    """Represent a node with exact numerical precision.

    This class inherits from `Node` and implements a more precise version of
    addition to fix discrepancies with floating point numbers.
    """

    @property
    def now(self) -> Decimal:
        """Get the current simulation time.

        Returns:
            Decimal: The current simulation time.
        """
        return Decimal(self.simulation.current_time)

    def create_starting_servers(self) -> list[Server]:
        """Initialise the servers at this node.

        Returns:
            List[Server]: The newly created starting servers.
        """
        return [Server(self, i + 1, Decimal("0.0")) for i in range(int(self.c))]

    def increment_time(self, original, increment) -> Decimal:
        """Increment the original time by the increment.

        Args:
            original (float): The original time.
            increment (float): The amount to add.

        Returns:
            Decimal: The incremented time.
        """
        return Decimal(str(original)) + Decimal(str(increment))

    def get_service_time(self, ind) -> Decimal:
        """Return a service time for the given customer class.

        Args:
            ind (Individual): The individual being served.

        Returns:
            Decimal: The sampled service time.
        """
        return Decimal(
            str(
                self.simulation.service_times[self.id_number][
                    ind.customer_class
                ]._sample(self.simulation.current_time, ind=ind)
            )
        )


class ExactArrivalNode(ArrivalNode):
    """Represent an arrival node with exact numerical precision.

    Inherits from `ArrivalNode` and implements a more precise version of
    addition to fix discrepancies with floating point numbers.
    """

    def increment_time(self, original, increment) -> Decimal:
        """Increment the original time by the increment.

        Args:
            original (float): The original time.
            increment (float): The amount to add.

        Returns:
            Decimal: The incremented time.
        """
        return Decimal(str(original)) + Decimal(str(increment))

    def inter_arrival(self, nd, clss) -> Decimal:
        """Sample the inter-arrival time for the next class and node.

        Args:
            nd (Node): The next node.
            clss (Individual): The individual class to select next.

        Returns:
            Decimal: The sampled inter-arrival time.
        """
        return Decimal(
            str(
                self.simulation.inter_arrival_times[nd][clss]._sample(
                    self.simulation.current_time
                )
            )
        )
