from enum import Enum
from typing import List, Dict
from collections import OrderedDict
from transitions import Machine
from transitions.core import EventData
from uuid import uuid4
from .clock import Clock
from .loggers import get_simobility_logger


class StateMachine:

    """ Basic class for all classes with multiple states, e.g. Booking, Vehicle.

    The main responcibility of this class is to log all state transitions.
    When state is changes `_state_machine` calls method `on_state_changed`.

    All chagnes are loged by `logger`
    """

    def __init__(
        self,
        clock: Clock,
        transitions: List[List[object]],
        states: List[Enum],
        initial_state: Enum,
        object_id: str = None,
    ):
        self.id = object_id
        if self.id is None:
            self.id = uuid4().hex
        self.clock = clock
        self.created_at = clock.now

        self._state_machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=initial_state,
            send_event=True,
            after_state_change="on_state_changed",
        )

        self.logger = get_simobility_logger()

    def on_state_changed(self, event: EventData) -> Dict:
        """Called on each state transition"""

        state_info = self.process_state_change(event)

        # Check Booking.on_state_changed and Vehicle.on_state_changed for details
        # msg = self.format_message(state_info)

        # Log state changes - results of simulations
        self.logger.info(state_info)

        return state_info


    def process_state_change(self, event: EventData) -> OrderedDict:
        # Arguments specific to each class and state change
        # They defined in derived classes
        arguments = event.kwargs.copy()

        tid = None
        itinerary = arguments.get("itinerary")
        if itinerary:
            tid = itinerary.id
            del arguments["itinerary"]

        # every change should have position
        position = arguments["position"]
        del arguments["position"]

        state_info = OrderedDict()
        state_info["clock_time"] = self.clock.now
        state_info["object_type"] = self.__class__.__name__.lower()
        state_info["uuid"] = self.id
        # itinerary id
        state_info["itinerary_id"] = tid
        # from state
        state_info["from_state"] = event.transition.source
        # to state
        state_info["to_state"] = event.transition.dest
        state_info["lon"] = position["lon"]
        state_info["lat"] = position["lat"]
        state_info["details"] = arguments

        return state_info
