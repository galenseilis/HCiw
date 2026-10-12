"""Server that processes individuals at a node."""


class Server(object):
    """Contain information about a server."""

    def __init__(self, node, id_number, start_date=0.0):
        """Initialise the server.

        Args:
            node (Node): The node the server belongs to.
            id_number (int): Identifier for the server.
            start_date (float): The time at which the server started.
        """
        self.node = node
        self.id_number = id_number
        self.cust = False
        self.busy = False
        self.offduty = False
        self.all_time = False
        self.start_date = start_date
        self.busy_time = False
        self.total_time = False
        self.shift_end = False
        self.next_end_service_date = float("Inf")
        self.busy_time = 0.0

    @property
    def utilisation(self):
        """Get the server utilisation.

        Returns:
            float: The proportion of total time the server was busy.
        """
        return self.busy_time / self.total_time

    def __repr__(self):
        """Return a string representation of the server.

        Returns:
            str: The representation of the server.
        """
        return "Server %s at Node %s" % (self.id_number, self.node.id_number)
