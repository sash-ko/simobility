import pytest
from simobility.core import Itinerary, Clock


def test_create():
    vehicle = '111'
    clock = Clock()
    clock.tick()
    clock.tick()
    itinerary = Itinerary(clock.now, vehicle)

    assert itinerary.created_at == clock.now
    assert itinerary.next_jobs == []
    assert itinerary.current_job is None
    assert itinerary.jobs_to_complete == []
    assert not itinerary.is_completed()
    assert itinerary.vehicle == vehicle


def test_add_jobs():
    itinerary = Itinerary(45, '2222')

    move_job = itinerary.move_to(123)
    current_job = itinerary.current_job
    assert move_job == current_job
    assert move_job is not None
    assert current_job is not None
    assert itinerary.next_jobs == []
    assert itinerary.jobs_to_complete == [current_job]
    assert not itinerary.is_completed()

    itinerary.pickup('1212')
    assert len(itinerary.next_jobs) == 1
    assert len(itinerary.jobs_to_complete) == 2
    assert itinerary.current_job == current_job
    assert not itinerary.is_completed()

    itinerary.dropoff('333')
    assert len(itinerary.next_jobs) == 2
    assert len(itinerary.jobs_to_complete) == 3
    assert itinerary.current_job == current_job
    assert not itinerary.is_completed()

    itinerary.wait(444)
    assert len(itinerary.next_jobs) == 3
    assert len(itinerary.jobs_to_complete) == 4
    assert itinerary.current_job == current_job
    assert not itinerary.is_completed()

    with pytest.raises(Exception):
        itinerary.add_job('Not a Base')


def test_job_complete():
    itinerary = Itinerary(234, '3434')

    move_job = itinerary.move_to(33)
    itinerary.job_complete(move_job)

    assert itinerary.is_completed()
    assert itinerary.current_job is None
    assert itinerary.completed_jobs == [move_job]

    pickup = itinerary.pickup('aaaa')
    assert itinerary.current_job == pickup
    assert not itinerary.is_completed()
    assert itinerary.jobs_to_complete == [pickup]
    assert itinerary.next_jobs == []

    dropoff = itinerary.dropoff('aaaa')
    move_job = itinerary.move_to(66666)

    assert itinerary.next_jobs == [dropoff, move_job]

    # jobs can be completed only in the order they planned
    with pytest.raises(Exception):
        itinerary.job_complete(dropoff)

    itinerary.job_complete(pickup)
    assert not itinerary.is_completed()
    assert itinerary.next_jobs == [move_job]
    assert itinerary.current_job == dropoff
    assert itinerary.jobs_to_complete == [dropoff, move_job]

    itinerary.job_complete(dropoff)
    itinerary.job_complete(move_job)
    assert itinerary.is_completed()


def test_job_types():
    created_at = 2
    itinerary = Itinerary(created_at, '343433')
    itinerary.created_at = created_at

    job = itinerary.pickup('34')
    assert job.name() == 'pickup'
    assert job.is_pickup()
    assert job.itinerary_id == itinerary.id

    job = itinerary.dropoff('33')
    assert job.name() == 'dropoff'
    assert job.is_dropoff()
    assert not job.is_pickup()
    assert job.itinerary_id == itinerary.id

    job = itinerary.move_to('33', 10)
    assert job.name() == 'move_to'
    assert job.is_move_to()
    assert not job.is_dropoff()
    assert not job.is_pickup()
    assert job.eta == 10
    assert job.itinerary_id == itinerary.id

    job = itinerary.wait('33')
    assert job.name() == 'wait'
    assert job.is_wait()
    assert not job.is_move_to()
    assert not job.is_dropoff()
    assert not job.is_pickup()
    assert job.itinerary_id == itinerary.id


def test_is_method():

    itinerary = Itinerary(123, '111')
    job = itinerary.move_to('111')

    assert not job.is_pickup()
    assert not job.is_dropoff()
    assert not job.is_wait()

    with pytest.raises(Exception):
        # is_moving job in not supported and should throw an exaption
        job.is_moving