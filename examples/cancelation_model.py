from scipy.stats import poisson
import numpy as np


class CustomerModel:

    def __init__(self, clock, avg_waiting_time):
        self.clock = clock
        self.avg_waiting_time = avg_waiting_time

    def filter(self, itineraries):
        non_canceled = []

        now = self.clock.clock_time
        for s in itineraries:
            if s.created_at != now:
                raise Exception('Created not now')

            self.validate(s)
            if not self.cancel(s):
                non_canceled.append(s)

        return non_canceled

    def cancel(self, itinerary):
        pickup_eta = 0
        for job in itinerary.jobs_to_complete:
            pickup_eta += job.eta
            if job.is_pickup:
                p = poisson.cdf(mu=self.avg_waiting_time, k=pickup_eta)
                if np.random.random() < p:
                    job.booking.set_customer_canceled()
                    return True
                break

    def validate(self, itinerary):
        # TODO: validate sequence of jobs
        pickup = None
        for job in itinerary.jobs_to_complete:
            if job.is_pickup:
                if pickup is None:
                    pickup = job
                else:
                    raise Exception('More than one pickup is not supported')
            elif job.is_dropoff and pickup and pickup.booking != job.booking:
                raise Exception('Booking ahead of pickup')
