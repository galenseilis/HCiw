from typing import List

import ciw
import numpy as np


def wait_time_over_benchmark(individuals: List[ciw.Individual]) -> ciw.Individual:
    """Service distribution that selects the individual
      the most over their benchmark.

      Requires that the individual's customer class has a numerical
      attribute "benchmark".

    Args:
      individuals (List[Individual]): The individuals in the simulation.

    Returns (ciw.Individual):
      Individual with the greatest time over their
    """

    idx = np.argmax(
        [ind.customer_class.benchmark - ind.arrival_date for ind in individuals]
    )

    return individuals[idx]
