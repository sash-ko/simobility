from typing import List, Callable, Dict
from uuid import uuid4
import logging
from .base_position import BasePosition
from .booking import Booking


class BaseJob:

    # A list of job names derived from the base class
    # The elements will be added at the bottom of the file
    supported_jobs: List[str] = []

    def __init__(self, itinerary_id):
        self.id = uuid4().hex
        self.itinerary_id = itinerary_id

    def to_dict(self) -> Dict:
        return {"itinerary_id": self.itinerary_id, "job_name": self.name()}

    @classmethod
    def name(cls):
        logging.error('Property "_name" is not implemented')

        raise NotImplementedError

    def __getattr__(self, key: str) -> Callable:
        """ Each job implements method `is_<job_name>`, for example, MoveTo.is_move_to 
        that return True. But, it is important that each job has a method `is_<other_job_name>`
        that returns False. In order to avoid users calling `is_` with wrong names this 
        method return lambda function that returns None. But to protect user from
        calling `is_<not_supported_name>` functions, __getattr__ with check it and throw
        and exception

        >> job = Dropoff(Booking, 10)
        >> print(job.is_dropoff())
        >> True
        >> print(job.is_pickup())
        >> False
        >> print(job.is_sleep())
        >> Exception

        """

        # If job name is not supported throw an exception
        # otherwise just return False
        if key.startswith("is_") and key.split("_", 1)[-1] not in self.supported_jobs:
            raise Exception(f"Job {key.split('_', 1)[-1]} if not supported")

        return lambda: False

    def __str__(self):
        return f"Job {self.name()} (id={self.id})"


class MoveTo(BaseJob):
    def __init__(self, itinerary_id: str, destination: BasePosition):
        super().__init__(itinerary_id)
        self.destination = destination

    def is_move_to(self) -> bool:
        return True

    @classmethod
    def name(cls):
        return "move_to"

    def to_dict(self) -> Dict:
        d = super().to_dict()
        d["destination"] = self.destination
        return d


class Pickup(BaseJob):
    def __init__(self, itinerary_id: str, booking: Booking):
        super().__init__(itinerary_id)
        self.booking = booking

    @classmethod
    def name(cls):
        return "pickup"

    def is_pickup(self) -> bool:
        return True


class Dropoff(BaseJob):
    def __init__(self, itinerary_id: str, booking: Booking):
        super().__init__(itinerary_id)
        self.booking = booking

    def is_dropoff(self) -> bool:
        return True

    @classmethod
    def name(cls):
        return "dropoff"


class Wait(BaseJob):
    def __init__(self, itinerary_id: str, duration: int):
        super().__init__(itinerary_id)
        self.duration = duration

    def is_wait(self) -> bool:
        return True

    @classmethod
    def name(cls):
        return "wait"


# Discovers all jobs derived from the Base class
# NOTE: this _must_ remain at the end of the file!
BaseJob.supported_jobs = [cls.name() for cls in BaseJob.__subclasses__()]
