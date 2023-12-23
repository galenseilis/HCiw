"""Server schedules or factories of schedules."""

from typing import List

def weekday_server_sched(offset: float = 0) -> List[List[float]]:
    """
    Generates a schedule indicating weekdays based on a given offset.

    Args:
        offset (float, optional): The number of days to offset the schedule. Defaults to 0.

    Returns:
        List[List[float]]: A list of lists, where each inner list contains two elements:
            - The first element (float): 1 if the corresponding day is a weekday (Monday to Friday),
              and 0 otherwise.
            - The second element (float): The day index incremented by 1.

    Example:
        >>> weekday_server_sched(2)
        [[0, 1], [0, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7]]

        This example generates a schedule with a 2-day offset, where days 3 to 7 are considered weekdays.
    """
    return [[1 if ((i - offset + 7) % 7) < 5 else 0, i+1] for i in range(7)]

