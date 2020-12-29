from .booking import Booking
from .itinerary import Itinerary


def do_job(itinerary: Itinerary):
    """ The core of each simulation - executes a sequence of steps grouped
    in itineraries.
    """

    current_job = itinerary.current_job
    if not current_job:
        return

    if current_job.is_pickup():
        booking = current_job.booking

        if pickup_booking(booking, itinerary):
            itinerary.job_complete(current_job)
            do_job(itinerary)

    elif current_job.is_dropoff():
        booking = current_job.booking

        if dropoff_booking(booking, itinerary):
            itinerary.job_complete(current_job)
            do_job(itinerary)

    elif current_job.is_move_to():
        # if current job is move_to but after but vehicle is not
        # moving after the move_vehicle call, this mean that vehicle
        # has arrived and the job can be considered done
        if not move_vehicle(itinerary):
            itinerary.job_complete(current_job)
            do_job(itinerary)

    elif current_job.is_wait():
        # TODO: for how long ??????
        # vehicle.stop()

        raise NotImplementedError()
    else:
        raise Exception(f"Unknown job: {current_job}")


def move_vehicle(itinerary: Itinerary) -> bool:
    """Assumes that the current job of the itinerary is MoveTo and move vehicle to the
    destination specified in the job description"""

    current_job = itinerary.current_job
    if current_job is None:
        raise Exception("Current job cannot be None")

    vehicle = itinerary.vehicle

    vehicle.move_to(current_job.destination, itinerary=itinerary)

    return vehicle.is_moving


def pickup_booking(booking: Booking, itinerary: Itinerary) -> bool:
    """Assumes that the current job is Pickup and updates the booking state"""

    if booking.is_pending():
        # when pickup is the first step in the itinerary
        # otherwise update_bookings_states changes booking state
        # to matched
        booking.set_matched(itinerary=itinerary)

    if booking.is_matched():
        # TODO: how to test 2 state changes in one function?
        # pickup immediately
        booking.set_waiting_pickup(itinerary=itinerary)
        booking.set_pickup(itinerary=itinerary)

    elif booking.is_waiting_pickup():
        booking.set_pickup(itinerary=itinerary)

    elif booking.is_customer_canceled():
        # TODO: what to do??
        raise NotImplementedError()

    elif booking.is_dispatcher_canceled():
        # TODO: what to do??
        raise NotImplementedError()
    else:
        raise Exception(f"Invalid state for pickup: {booking.state}")

    return booking.is_pickup()


def dropoff_booking(booking: Booking, itinerary: Itinerary) -> bool:
    """Assumes that the current job is Pickup and updates the booking state"""

    # if booking.is_matched() or booking.is_waiting_pickup():
    # raise Exception('Cannot dropoff booking without pickup')
    if booking.is_waiting_dropoff():
        # TODO: how to test 2 state changes in one function?
        booking.set_dropoff(itinerary=itinerary)
        booking.set_complete(itinerary=itinerary)

    elif booking.is_pickup():
        booking.set_waiting_dropoff(itinerary=itinerary)
        booking.set_dropoff(itinerary=itinerary)
        booking.set_complete(itinerary=itinerary)
    else:
        raise Exception(f"Invalid state for dropoff: {booking.state}")

    return booking.is_complete()


def update_next_bookings(itinerary: Itinerary) -> None:
    """Change jobs after the current one and change booking states"""

    # context = itinerary_info(itinerary)
    # TODO: expired or canceled bookings
    jobs = itinerary.next_jobs
    for job in jobs:
        if job.is_pickup():
            booking = job.booking
            if booking.is_pending():
                booking.set_matched(itinerary=itinerary)
                booking.set_waiting_pickup(itinerary=itinerary)

        elif job.is_dropoff():
            booking = job.booking
            if booking.is_pickup():
                booking.set_waiting_dropoff(itinerary=itinerary)


# def itinerary_info(itinerary: Itinerary) -> Dict:
#     return {
#         "vid": itinerary.vehicle.id,
#         "it_id": itinerary.id,
#         # "it_time": itinerary.created_at,
#     }
