"""Computing results from simulations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Hashable

import ciw
import numpy as np
import pandas as pd


def summarize_individuals(
    simulation: ciw.Simulation,
    time: float,
    agg_f: Callable,
    desc_f: Callable,
    filter_f: Callable = None,
) -> Any:
    """
    Summarizes individual-level information in a simulation.

    Args:
        simulation: The simulation instance containing node and individual information.
        time: The current time in the simulation.
        agg_f (function): The aggregation function to apply on individual-level descriptors.
        desc_f (function): The function to generate a descriptor for each individual.
        filter_f (function, optional): The filter function to selectively include individuals. Defaults to None.

    Returns:
        dict: A dictionary summarizing aggregated information for each simulation node.

    Notes:
        - The function iterates through non-terminal simulation nodes (excluding the initial and final nodes).
        - For each node, it aggregates descriptors of filtered individuals using the provided aggregation function.
        - The resulting summary is stored in a dictionary, where keys are node names, and values are aggregated descriptors.
        - If a node has no individuals, it is assigned a default value of 1 in the summary.
        - The `filter_f` function is optional and can be used to selectively include individuals in the summary.

    Examples:
        >>> simulation_instance = ciw.Simulation()
        >>> time_point = 10.0
        >>> aggregation_function = np.mean
        >>> descriptor_function = lambda ind, t: ind.service_time
        >>> filter_function = lambda ind, t: ind.arrival_date < t
        >>> result_summary = summarize_individuals(simulation_instance, time_point,
        ...                                       aggregation_function, descriptor_function, filter_function)
        >>> print(result_summary)
        {'Node_1': 5.0, 'Node_2': 8.0, ...}

    """
    filter_f = filter_f or (lambda x, t: True)
    result = {}
    for node in simulation.nodes[1:-1]:
        if node.all_individuals:
            pub = agg_f(
                [desc_f(ind, time) for ind in node.all_individuals if filter_f(ind, time)]
            )
            result[str(node)] = pub if np.isfinite(pub) else 1
        else:
            result[str(node)] = 1
    return result


def is_under_benchmark(ind: ciw.Individual, t: float) -> bool:
    """
    Checks if an individual's service time is under their benchmark at a given time.

    Args:
        ind (ciw.Individual): The individual for which the check is performed.
        t (float): The current time in the simulation.

    Returns:
        bool: True if the individual's service time is under their benchmark, False otherwise.

    Notes:
        - The function compares the sum of the individual's arrival date and benchmark
          with the current time to determine if the individual is under their benchmark.
        - Returns True if the individual is under their benchmark, indicating favorable performance.
        - Returns False if the individual's service time has exceeded their benchmark.

    Examples:
        >>> individual_instance = ciw.Individual(id_number=1, customer_class=Class_A, simulation=simulation_instance)
        >>> current_time = 15.0
        >>> result_check = is_under_benchmark(individual_instance, current_time)
        >>> print(result_check)
        False

    """
    return t <= (ind.arrival_date + ind.customer_class.benchmark)


def least_percent_underbenchmark(simulation: ciw.Simulation, t: float = None) -> float:
    """
    Calculates the least percentage of individuals under their benchmark across all simulation nodes.

    Args:
        simulation (ciw.Simulation): The simulation instance containing node and individual information.
        t (float, optional): The time at which to calculate the percentage. Defaults to None, using the current time.

    Returns:
        float: The least percentage of individuals under their benchmark across all nodes.

    Notes:
        - The function utilizes the `summarize_individuals` function to obtain a summary of aggregated information
          for each simulation node.
        - The `is_under_benchmark` function is used as the descriptor function to determine if an individual is under their benchmark.
        - The least percentage across all nodes is calculated using the provided aggregation function (`np.mean`).

    Examples:
        >>> simulation_instance = ciw.Simulation()
        >>> time_point = 10.0
        >>> least_percent = least_percent_underbenchmark(simulation_instance, t=time_point)
        >>> print(least_percent)
        0.75

    """
    t = t or simulation.current_time
    return min(
        summarize_individuals(
            simulation, time=t, agg_f=np.mean, desc_f=is_under_benchmark
        ).values()
    )


def is_urgent(ind: ciw.Individual, t: float = None) -> bool:
    """
    Checks if an individual is classified as urgent based on their priority.

    Args:
        ind (ciw.Individual): The individual for which the urgency is determined.
        t (float, optional): The current time in the simulation. Defaults to None.

    Returns:
        bool: True if the individual is classified as urgent (priority 0), False otherwise.

    Notes:
        - The function checks the priority class of the individual to determine urgency.
        - Returns True if the individual is classified as urgent (priority 0), indicating high priority.
        - Returns False if the individual does not fall into the urgent priority class.

    Examples:
        >>> individual_instance = ciw.Individual(id_number=1, customer_class=Class_A, simulation=simulation_instance)
        >>> is_urgent_check = is_urgent(individual_instance)
        >>> print(is_urgent_check)
        False

    """
    return ind.customer_class.priority == 0


def least_percent_urgent_underbenchmark(
    simulation: ciw.Simulation, t: float = None
) -> float:
    """
    Calculates the least percentage of urgent individuals under their benchmark across all simulation nodes.

    Args:
        simulation (ciw.Simulation): The simulation instance containing node and individual information.
        t (float, optional): The time at which to calculate the percentage. Defaults to None, using the current time.

    Returns:
        float: The least percentage of urgent individuals under their benchmark across all nodes.

    Notes:
        - The function utilizes the `summarize_individuals` function to obtain a summary of aggregated information
          for each simulation node.
        - The `is_under_benchmark` function is used as the descriptor function to determine if an individual is under their benchmark.
        - The `is_urgent` function is used as the filter function to include only urgent individuals in the summary.
        - The least percentage across all nodes is calculated using the provided aggregation function (`np.mean`).

    Examples:
        >>> simulation_instance = ciw.Simulation()
        >>> time_point = 10.0
        >>> least_percent_urgent = least_percent_urgent_underbenchmark(simulation_instance, t=time_point)
        >>> print(least_percent_urgent)
        0.65

    """
    t = t or simulation.current_time
    return min(
        summarize_individuals(
            simulation,
            time=t,
            agg_f=np.mean,
            desc_f=is_under_benchmark,
            filter_f=is_urgent,
        ).values()
    )


def fiscal_year(date_time: datetime) -> int:
    """
    Determines the fiscal year based on the provided date and time.

    Args:
        date_time (datetime): A datetime object representing the date and time.

    Returns:
        int: The fiscal year associated with the given date and time.

    Notes:
        - The function calculates the fiscal year by checking if the month in the provided date is after March (month 3).
        - If the month is after March, the fiscal year is incremented by 1.
        - The resulting fiscal year is returned as an integer.

    Examples:
        >>> input_date = datetime(2023, 8, 15)
        >>> fiscal_year_result = fiscal_year(input_date)
        >>> print(fiscal_year_result)
        2024
    """
    year = date_time.year
    if date_time.month > 3:
        year += 1
    return year


def convert_simtime_to_datetime(base_datetime: datetime, t: float) -> datetime:
    """
    Converts simulation time to a datetime object.

    Args:
        base_datetime (datetime): The base datetime to start from.
        t (float): The simulation time to be added in days.

    Returns:
        datetime: A new datetime object representing the result of adding simulation time to the base datetime.

    Examples:
        >>> base_date = datetime(2023, 1, 1)
        >>> simulation_time = 5.5  # 5.5 days
        >>> result_datetime = convert_simtime_to_datetime(base_date, simulation_time)
        >>> print(result_datetime)
        2023-01-06 12:00:00
    """
    return base_datetime + pd.Timedelta(t, "D")


# TODO: Convert to full time resolution (i.e.
def convert_datetime_to_simtime(start_time: datetime, datetime_value: datetime) -> int:
    """
    Converts a datetime object to simulation time in days relative to a specified start time.

    Args:
        start_time (datetime): The reference datetime to calculate the time difference.
        datetime_value (datetime): The datetime value to convert to simulation time.

    Returns:
        int: The simulation time in days relative to the specified start time.

    Examples:
        >>> start_date = datetime(2023, 1, 1)
        >>> target_date = datetime(2023, 1, 10)
        >>> simtime_result = convert_datetime_to_simtime(start_date, target_date)
        >>> print(simtime_result)
        9
    """
    return (datetime_value - start_time).days


def filter_to_cover_time(df: pd.DataFrame, t: float) -> pd.DataFrame:
    """
    Filters a DataFrame to include rows covering a specific time.

    Args:
        df (pd.DataFrame): The DataFrame to be filtered.
        t (float): The specific time to filter for.

    Returns:
        pd.DataFrame: A new DataFrame containing rows where the arrival_date is less than or equal to `t`
                      and the exit_date is greater than or equal to `t`.

    Examples:
        >>> input_df = pd.DataFrame({'arrival_date': [1.0, 2.0, 3.0],
        ...                           'exit_date': [4.0, 5.0, 6.0],
        ...                           'other_column': ['A', 'B', 'C']})
        >>> target_time = 3.5
        >>> result_df = filter_to_cover_time(input_df, target_time)
        >>> print(result_df)
           arrival_date  exit_date other_column
        0           1.0        4.0            A
        1           2.0        5.0            B
    """
    return df[(df["arrival_date"] <= t) & (df["exit_date"] >= t)]


def fiscal_year_date_range(start_date: datetime, end_date: datetime) -> list:
    """
    Generates a list of fiscal year end dates within a specified date range.

    Args:
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.

    Returns:
        list: A list of fiscal year end dates represented as pandas Timestamp objects.

    Examples:
        >>> start_date = datetime(2022, 1, 1)
        >>> end_date = datetime(2024, 12, 31)
        >>> result_dates = fiscal_year_date_range(start_date, end_date)
        >>> print(result_dates)
        [Timestamp('2022-03-31 00:00:00'), Timestamp('2023-03-31 00:00:00'), Timestamp('2024-03-31 00:00:00')]
    """
    return [
        pd.to_datetime(f"{year}-03-31")
        for year in range(start_date.year, end_date.year + 1)
    ]


def fiscal_year_simtimes(start_date: datetime, end_date: datetime) -> list:
    """
    Converts fiscal year end dates to simulation times within a specified date range.

    Args:
        start_date (datetime): The start date of the date range.
        end_date (datetime): The end date of the date range.

    Returns:
        list: A list of simulation times representing the number of days from the start_date.

    Examples:
        >>> start_date = datetime(2022, 1, 1)
        >>> end_date = datetime(2024, 12, 31)
        >>> result_simtimes = fiscal_year_simtimes(start_date, end_date)
        >>> print(result_simtimes)
        [89, 454, 818]
    """
    return [
        convert_datetime_to_simtime(start_date, date)
        for date in fiscal_year_date_range(start_date, end_date)
    ]

def expand_dataclass_column(dataclass_class: dataclass, dataframe: pd.DataFrame, dataframe_column: Hashable) -> pd.DataFrame:
	'''Expand a column of dataclasses into multiple dataframe columns.

	Args:
		dataclass_class (dataclass): A dataclass.
		dataframe (pandas.DataFrame): Dataframe with a column of dataclass instances to be expanded.
		dataframe_column (str | hashble): Column containing dataclasses.

	Returns:
		expanded_dataframe (pandas.DataFrame): Expanded dataframe.
		'''	
	for attribute_name in dataclass_class.__annotations__:
		dataframe[attribute_name] = dataframe[dataframe_column].apply(
			lambda dataclass_instance: getattr(dataclass_instance, attribute_name)
		)

	expanded_dataframe = dataframe.drop(dataframe_column, axis=1)

	return expanded_dataframe

