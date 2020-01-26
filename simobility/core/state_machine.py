from enum import Enum
import json
from typing import List, Dict
from collections import OrderedDict
from transitions import Machine
from transitions.core import EventData
from uuid import uuid4
import logging
from .clock import Clock

# WARNING: do not change is line otherwise simulation logs can disappear
simulation_logs = logging.getLogger("state_changes")


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

    def on_state_changed(self, event: EventData) -> Dict:
        """Called on each state transition"""

        state_info = self.process_state_change(event)

        # Check Booking.on_state_changed and Vehicle.on_state_changed for details
        msg = self.format_message(state_info)

        # Log state changes - results of simulations
        simulation_logs.debug(msg)

        return state_info

    def format_message(self, state_info: OrderedDict) -> str:
        strings = []
        for item in state_info.values():
            try:
                if item is None:
                    item = ""
                elif isinstance(item, dict):
                    item = json.dumps(item, separators=(",", ":"))
                else:
                    item = str(item)
            # catche error json.encoder.JSONEncoder
            except TypeError:
                item = str(item)

            strings.append(item)

        msg = ";".join(strings)
        return msg

    def process_state_change(self, event: EventData) -> OrderedDict:
        # Arguments specific to each class and state change
        # They defined in derived classes
        arguments = event.kwargs.copy()

        # each message should contain itinerary id
        tid = arguments.get("it_id")
        if tid:
            del arguments["it_id"]

        # every change should have position
        position = arguments["position"]
        del arguments["position"]

        class_ = self.__class__.__name__.lower()
        if class_ == "vehicle" and arguments.get("vid") is not None:
            del arguments["vid"]

        source = event.transition.source
        dest = event.transition.dest

        state_info = OrderedDict()
        state_info["clock"] = self.clock.now
        state_info["class"] = class_
        state_info["id"] = self.id
        # itinerary id
        state_info["it_id"] = tid
        # from state
        state_info["source"] = source
        # to state
        state_info["dest"] = dest
        state_info["lon"] = position["lon"]
        state_info["lat"] = position["lat"]
        state_info["arguments"] = arguments

        return state_info
