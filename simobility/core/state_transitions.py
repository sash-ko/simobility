from typing import Dict
from .vehicle import Vehicle
from .booking import Booking
from .itinerary import Itinerary


def do_job(itinerary: Itinerary):
    """ The core of the simulation"""

    current_job = itinerary.current_job
    if not current_job:
        return

    if current_job.is_pickup():
        booking = current_job.booking

        if pickup_booking(booking, itinerary_info(itinerary)):
            itinerary.job_complete(current_job)
            do_job(itinerary)

    elif current_job.is_dropoff():
        booking = current_job.booking

        if dropoff_booking(current_job.booking, itinerary_info(itinerary)):
            itinerary.job_complete(current_job)
            do_job(itinerary)

    elif current_job.is_move_to():
        if not move_vehicle(itinerary.vehicle, itinerary):
            itinerary.job_complete(current_job)
            do_job(itinerary)

    elif current_job.is_wait():
        # TODO: for how long ??????
        # vehicle.stop()

        raise NotImplementedError()
    else:
        raise Exception(f"Unknown job: {current_job._name}")


def move_vehicle(vehicle: Vehicle, itinerary: Itinerary) -> bool:
    """"""
    current_job = itinerary.current_job
    if not current_job:
        raise Exception("Current job cant be None")

    context = itinerary_info(itinerary)
    if current_job.eta is not None:
        context["eta"] = current_job.eta

    if itinerary.next_jobs:
        job = itinerary.next_jobs[0]

        if job.is_pickup():
            context["pickup"] = job.booking.id

        elif job.is_dropoff():
            context["dropoff"] = job.booking.id

    vehicle.move_to(current_job.destination, context)

    return vehicle.is_moving


def pickup_booking(booking: Booking, context: Dict) -> bool:
    if booking.is_pending():
        # when pickup is the first step in the itinerary
        # otherwise update_bookings_states changes booking state
        # to matched
        booking.set_matched(**context)

    if booking.is_matched():
        # TODO: how to test 2 state changes in one function?
        # pickup immediately
        booking.set_waiting_pickup(**context)
        booking.set_pickup(**context)

    elif booking.is_waiting_pickup():
        booking.set_pickup(**context)

    elif booking.is_customer_canceled():
        # TODO: what to do??
        raise NotImplementedError()

    elif booking.is_dispatcher_canceled():
        # TODO: what to do??
        raise NotImplementedError()
    else:
        raise Exception(f"Invalid state for pickup: {booking.state}")

    return booking.is_pickup()


def dropoff_booking(booking: Booking, context: Dict) -> bool:
    # if booking.is_matched() or booking.is_waiting_pickup():
    # raise Exception('Cannot dropoff booking without pickup')
    if booking.is_waiting_dropoff():
        # TODO: how to test 2 state changes in one function?
        booking.set_dropoff(**context)
        booking.set_complete(**context)

    elif booking.is_pickup():
        booking.set_waiting_dropoff(**context)
        booking.set_dropoff(**context)
        booking.set_complete(**context)
    else:
        raise Exception(f"Invalid state for dropoff: {booking.state}")

    return booking.is_complete()


def update_next_bookings(itinerary: Itinerary) -> None:
    """Change jobs after the current one and change booking
    states
    """

    context = itinerary_info(itinerary)
    # TODO: expired or canceled bookings
    jobs = itinerary.next_jobs
    for job in jobs:
        if job.is_pickup():
            booking = job.booking
            if booking.is_pending():
                booking.set_matched(**context)
                booking.set_waiting_pickup(**context)

        elif job.is_dropoff():
            booking = job.booking
            if booking.is_pickup():
                booking.set_waiting_dropoff(**context)



def itinerary_info(itinerary: Itinerary) -> Dict:
    return {
        "vid": itinerary.vehicle.id,
        "it_id": itinerary.id,
        # "it_time": itinerary.created_at,
    }
