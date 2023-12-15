from typing import List

import ciw
import numpy as np


def wait_time_over_benchmark(individuals: List[ciw.Individual]) -> ciw.Individual:
    """Selects the individual with the greatest time over their benchmark.

    Requires that the individual's customer class has a numerical attribute "benchmark".

    Args:
        individuals (List[ciw.Individual]): The list of individuals in the node.

    Returns:
        ciw.Individual: The individual with the greatest time over their benchmark.

    Raises:
        No specific exceptions are raised.

    Notes:
        - The function calculates the wait time over benchmark for each individual in the list.
        - The wait time over benchmark is computed as the difference between the current simulation time
          and the sum of the individual's benchmark and arrival date.
        - The individual with the maximum wait time over benchmark is selected and returned.
        - Requires that the customer class of each individual has a numerical attribute "benchmark".

    Examples:
        >>> individuals_list = [individual_1, individual_2, individual_3]
        >>> result_individual = wait_time_over_benchmark(individuals_list)
        >>> print(result_individual)
        <ciw.Individual object at 0x...>

    """

    current_time = individuals[0].simulation.current_time

    idx = np.argmax(
        [
            current_time - (ind.customer_class.benchmark + ind.arrival_date)
            for ind in individuals
        ]
    )

    return individuals[idx]


def lex_priority_benchmark_with_threshold_switch(
    individuals: List[ciw.Individual], threshold=0.8
) -> ciw.Individual:
    """Service top-priority individuals relative to benchmark; else, service based on benchmark.

    Args:
        individuals (List[ciw.Individual]): The list of individuals in the node.
        threshold (float, optional): The threshold for determining when to switch to servicing
            based on benchmark alone. Defaults to 0.8.

    Returns:
        ciw.Individual: The selected individual to be serviced next.

    Raises:
        No specific exceptions are raised.

    Notes:
        - The function first calculates an indicator of which top-priority individuals are under their benchmark.
        - Top-priority individuals are those with priority class 0.
        - If enough of the top-priority individuals are under their benchmark (above the threshold),
          the function selects and returns the individual with the greatest wait time over benchmark
          among the top-priority individuals.
        - If not enough top-priority individuals are under their benchmark, the function selects and returns
          the individual with the greatest wait time over benchmark among all individuals.

    Examples:
        >>> individuals_list = [individual_1, individual_2, individual_3]
        >>> result_individual = lex_priority_benchmark_with_threshold_switch(individuals_list, threshold=0.8)
        >>> print(result_individual)
        <ciw.Individual object at 0x...>

    """

    current_time = individuals[0].simulation.current_time

    # Calculate indicator of which top-priority individuals are under their benchmark.
    top_priority_under_bench = [
        current_time <= (ind.customer_class.benchmark + ind.arrival_date)
        for ind in individuals
        if ind.customer_class.priority == 0
    ]

    # Service top-priority individual who is most over thier benchmark if
    # not enough of the top-priority individuals under their benchmark.
    if top_priority_under_bench and np.mean(top_priority_under_bench) < threshold:
        top_priority_inds = [
            ind for ind in individuals if ind.customer_class.priority == 0
        ]
        return wait_time_over_benchmark(top_priority_inds)

    # Service individual latest in their service relative to their benchmark.
    return wait_time_over_benchmark(individuals)
