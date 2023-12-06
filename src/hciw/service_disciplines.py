from typing import List

import ciw
import numpy as np


def wait_time_over_benchmark(individuals: List[ciw.Individual]) -> ciw.Individual:
    """Service distribution that selects the individual
      the most over their benchmark.

    Requires that the individual's customer class has a numerical
      attribute "benchmark".

    Args:
        individuals (List[Individual]): The individuals in the node.

    Returns (ciw.Individual):
        Individual with the greatest time over their benchmark.
    """

    current_time = individuals[0].simulation.current_time
    
    # Ignore current_time since it cancels in the difference.
    idx = np.argmax(
        [
            (current_time - ind.arrival_date)
            - (ind.customer_class.benchmark + ind.arrival_date)
            for ind in individuals
        ]
    )

    return individuals[idx]


def lex_priority_benchmark_with_threshold_switch(
    individuals: List[ciw.Individual], threshold=0.8
) -> ciw.Individual:
    '''Service top-priority individuals relative to benchmark else just relative to benchmark.


    Args:
        individuals (List[Individual]): The individuals in the node.

    Returns (ciw.Individual):
        Selected invidual to be serviced next.
    '''

    current_time = individuals[0].simulation.current_time

    # Calculate indicator of which top-priority individuals are under their benchmark.
    top_priority_under_bench = [
        (current_time - ind.arrival_date)
        <= (ind.customer_class.benchmark + ind.arrival_date)
        for ind in individuals
        if ind.customer_class.priority_class == 0
    ]

    # Service top-priority individual who is most over thier benchmark if
    # not enough of the top-priority individuals under their benchmark.
    if top_priority_under_bench and np.mean(top_priority_under_bench) < threshold:
        top_priority_inds = [ind for ind in individuals if ind.customer_class.priority_class == 0]
        return wait_time_over_benchmark(top_priority_inds)

    # Service individual latest in their service relative to their benchmark.
    return wait_time_over_benchmark(individuals)
