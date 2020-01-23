from typing import List, Optional
from uuid import uuid4
import logging
from .vehicle import Vehicle
from .booking import Booking
from .position import Position
from .jobs import BaseJob, Pickup, MoveTo, Dropoff, Wait

# TODO: implement wait job using created_at and duration


class Itinerary:
    """ Define and store a request of jobs that will be
    run by a simulator:

    >> it = Itinerary('1223', 10)
    >> job = it.move_to('distination1')
    >> job.is_move_to
    True
    >> job = it.pickup('booking')
    """

    def __init__(self, created_at: int, vehicle: Vehicle):
        self.id: str = uuid4().hex
        self.vehicle = vehicle

        # [next_jobs] -> current_job -> [completed_jobs]
        self.current_job: Optional[BaseJob] = None
        self.next_jobs: List[BaseJob] = []
        self.completed_jobs: List[BaseJob] = []

        self.created_at: int = created_at

    def move_to(self, destination: Position, eta: int = None) -> BaseJob:
        """Create a move job - move vehicle to a specific position defined by 
        `destination`. `eta` is just an estimate used only for logging
        """
        return self.add_job(MoveTo(self.id, destination, eta))

    def pickup(self, booking: Booking, eta: int = None) -> BaseJob:
        return self.add_job(Pickup(self.id, booking, eta))

    def dropoff(self, booking: Booking, eta: int = None) -> BaseJob:
        return self.add_job(Dropoff(self.id, booking, eta))

    def wait(self, duration: int, eta: int = None) -> BaseJob:
        return self.add_job(Wait(self.id, duration, eta))

    def add_job(self, job: BaseJob) -> BaseJob:
        """Add job that was already created"""
        if not isinstance(job, BaseJob):
            raise Exception(f"Job {job} is not derived from Base")

        job.itinerary_id = self.id

        if self.current_job is None:
            self.current_job = job
        else:
            self.next_jobs.append(job)

        return job

    def job_complete(self, job: BaseJob):
        """Move current job to completed_jobs and replace it with the first
        job from the next jobs list
        """

        if job != self.current_job:
            raise Exception("Can not complete job which is not current")

        self.completed_jobs.append(job)
        self.current_job = None

        if self.next_jobs:
            self.current_job = self.next_jobs.pop(0)

    @property
    def jobs_to_complete(self) -> List[BaseJob]:
        """All jobs that are not completed - current + next_jobs"""

        next_jobs = self.next_jobs or []
        if self.current_job is not None:
            return [self.current_job] + next_jobs
        return []

    def is_completed(self) -> bool:
        """Returns true if there are no jobs to execute
        """

        return self.jobs_to_complete == []
