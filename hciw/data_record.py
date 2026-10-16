"""The data record stored for each visit of an individual to a node.

Attributes:
    id_number (int): Unique identifier of the individual.
    customer_class (str): The customer class of the individual.
    original_customer_class (str): The original customer class of the
        individual.
    node (int): The node the record refers to.
    arrival_date (float): The date the individual arrived at the node.
    waiting_time (float): The time the individual waited before service.
    service_start_date (float): The date service started.
    service_time (float): The duration of service.
    service_end_date (float): The date service ended.
    time_blocked (float): The time the individual spent blocked.
    exit_date (float): The date the individual left the node.
    destination (int): The destination node.
    queue_size_at_arrival (int): The queue size when the individual arrived.
    queue_size_at_departure (int): The queue size when the individual departed.
    server_id (int): The identifier of the server that served the individual.
    record_type (str): The type of record.
"""

from collections import namedtuple

# The ``"Record"`` typename is part of the observable behaviour (see
# ``tests/test_simulation.py``), so ``namedtuple`` is kept intentionally.
DataRecord = namedtuple(  # noqa: PYI024
    "Record",
    [
        "id_number",
        "customer_class",
        "original_customer_class",
        "node",
        "arrival_date",
        "waiting_time",
        "service_start_date",
        "service_time",
        "service_end_date",
        "time_blocked",
        "exit_date",
        "destination",
        "queue_size_at_arrival",
        "queue_size_at_departure",
        "server_id",
        "record_type",
    ],
)
