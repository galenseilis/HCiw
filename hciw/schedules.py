"""Server schedules for varying the number of servers over time."""

from collections.abc import Generator


class Schedule:
    """Store server schedule information and generate the next shifts.

    Attributes:
        schedule_type (str): The type of the schedule.
        shift_end_dates (List[float]): The end dates of each shift.
        numbers_of_servers (List[int]): The number of servers for each shift.
        preemption (Union[bool, str]): The pre-emption option.
        cyclelength (float): The length of the schedule cycle.
        offset (float): The offset applied to the schedule.
    """

    def __init__(
        self,
        numbers_of_servers: list[int],
        shift_end_dates: list[float],
        preemption: bool | str = False,
        offset: float = 0.0,
    ) -> None:
        """Initialise a ``Schedule`` instance.

        Args:
            numbers_of_servers (List[int]): The number of servers working at
                each shift.
            shift_end_dates (List[float]): The end dates of each shift.
            preemption (Union[bool, str], optional): The pre-emption option,
                one of ``'resume'``, ``'restart'``, ``'resample'``,
                ``'reroute'`` or ``False``. Defaults to ``False``.
            offset (float, optional): A non-negative offset applied to the
                schedule. Defaults to ``0.0``.

        Raises:
            ValueError: If ``preemption`` or ``offset`` is invalid.
        """
        if preemption not in [False, "resume", "restart", "resample", "reroute"]:
            raise ValueError(
                "Preemption must be False, 'resume', 'restart', "
                "'resample', 'reroute', or False."
            )
        if not isinstance(offset, float):
            raise ValueError(  # noqa: TRY004 - public API raises ValueError
                "Offset should be a positive float."
            )
        if offset < 0.0:
            raise ValueError("Offset should be a positive float.")
        self.schedule_type = "schedule"
        self.shift_end_dates = shift_end_dates
        self.numbers_of_servers = numbers_of_servers
        self.preemption = preemption
        self.cyclelength = self.shift_end_dates[-1]
        self.offset = offset

    def initialise(self) -> None:
        """Initialise the generator at the beginning of a simulation."""
        self.c = 0
        self.next_shift_change_date = self.offset
        self.next_c = self.numbers_of_servers[0]
        self.schedule_generator = self.get_schedule_generator(
            self.shift_end_dates, self.numbers_of_servers, self.offset
        )

    def get_schedule_generator(
        self, boundaries: list[float], values: list[int], offset: float
    ) -> Generator[tuple[float, int], None, None]:
        """Yield the next shift date and server count.

        Args:
            boundaries (List[float]): The shift boundaries.
            values (List[int]): The number of servers corresponding to each
                boundary.
            offset (float): The offset applied to the schedule.

        Yields:
            Tuple[float, int]: The next shift date and the number of servers.
        """
        num_boundaries = len(boundaries)
        index = 0
        date = 0
        while True:
            date = (
                offset
                + boundaries[index % num_boundaries]
                + ((index) // num_boundaries * self.cyclelength)
            )
            index += 1
            yield date, values[index % num_boundaries]

    def get_next_shift(self) -> None:
        """Update the next shift from the generator."""
        self.c = self.next_c
        date, c = next(self.schedule_generator)
        self.next_shift_change_date = date
        self.next_c = c


class Slotted(Schedule):
    """A schedule divided into slots with a number of servers per slot.

    Attributes:
        schedule_type (str): The type of the schedule.
        offset (float): The offset applied to the schedule.
        slots (list): The slot boundaries.
        slot_sizes (list): The number of servers in each slot.
        next_slot_sizes (list): The slot sizes of the next cycle.
        capacitated (bool): Whether the slots are capacitated.
        preemption (Union[bool, str]): The pre-emption option.
        cyclelength (float): The length of the schedule cycle.
        c (int): The current number of servers.
    """

    def __init__(
        self, slots, slot_sizes, capacitated=False, preemption=False, offset=0.0
    ):
        """Initialise a ``Slotted`` schedule instance.

        Args:
            slots (list): The slot boundaries.
            slot_sizes (list): The number of servers in each slot.
            capacitated (bool, optional): Whether the slots are capacitated.
                Defaults to ``False``.
            preemption (Union[bool, str], optional): The pre-emption option,
                one of ``'resume'``, ``'restart'``, ``'resample'`` or
                ``False``. Defaults to ``False``.
            offset (float, optional): A non-negative offset applied to the
                schedule. Defaults to ``0.0``.

        Raises:
            ValueError: If ``preemption`` or ``offset`` is invalid.
        """
        if not capacitated and preemption is not False:
            raise ValueError(
                "Pre-emption options not availale for non-capacitated slots."
            )
        if preemption not in [False, "resume", "restart", "resample"]:
            raise ValueError(
                "Pre-emption options should be either 'resume', 'restart', "
                "'resample', or False."
            )
        if not isinstance(offset, float):
            raise ValueError(  # noqa: TRY004 - public API raises ValueError
                "Offset should be a positive float."
            )
        if offset < 0.0:
            raise ValueError("Offset should be a positive float.")
        self.schedule_type = "slotted"
        self.offset = offset
        self.slots = slots
        self.slot_sizes = slot_sizes
        self.next_slot_sizes = [self.slot_sizes[-1], *self.slot_sizes[:-1]]
        self.capacitated = capacitated
        self.preemption = preemption
        self.cyclelength = self.slots[-1]
        self.c = 0

    def initialise(self):
        """Initialise the generator at the beginning of a simulation."""
        self.schedule_generator = self.get_schedule_generator(
            self.slots, self.next_slot_sizes, self.offset
        )
        self.get_next_slot()

    def get_next_slot(self):
        """Update the next slot date and size from the generator."""
        date, size = next(self.schedule_generator)
        self.next_slot_date = date
        self.slot_size = size
