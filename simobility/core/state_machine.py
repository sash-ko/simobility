from enum import Enum
from typing import List, Dict
from collections import OrderedDict
from transitions import Machine
from transitions.core import EventData
from uuid import uuid4
import logging
from .clock import Clock

logger = logging.getLogger("state_changes")


class StateMachine:
    def __init__(
        self,
        clock: Clock,
        transitions: List[List[object]],
        states: List[Enum],
        initial_state: Enum,
        object_id: str = None,
    ):
        self.id = object_id or uuid4().hex
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
        state_info = self.process_state_change(event)
        msg = self.format_message(state_info)

        logger.debug(msg)

        return state_info

    def format_message(self, state_info: OrderedDict) -> str:
        msg = ";".join([str(i) for i in state_info.values()])
        return msg

    def process_state_change(self, event: EventData) -> OrderedDict:
        arguments = event.kwargs

        tid = arguments.get("itinerary_id")

        class_ = self.__class__.__name__.lower()
        source = event.transition.source
        dest = event.transition.dest

        state_info = OrderedDict()
        state_info["clock"] = self.clock.now
        state_info["class"] = class_
        state_info["id"] = self.id
        state_info["tid"] = tid
        state_info["source"] = source
        state_info["dest"] = dest
        state_info["arguments"] = arguments

        return state_info
