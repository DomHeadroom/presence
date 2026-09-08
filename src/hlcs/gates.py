"""
Created on 08/nov/2014

@author: spax
"""

import re

from django.conf import settings

from gatecontrol.gatecontrol import STATE_CLOSED, STATE_OPEN, Gate
from hlcs.modem import AtlantisModem

STATE_RING = {"id": 2, "description": "ring"}
STATE_UNAVAILABLE = {"id": 3, "description": "unavailable"}


class HpccExternal(Gate):
    def __init__(self, modem=None):
        self.modem = modem

    def is_available(self):
        if self.modem is None:
            return AtlantisModem.is_available()
        return True

    def get_available_states(self):
        return (STATE_CLOSED, STATE_OPEN, STATE_RING, STATE_UNAVAILABLE)

    def open_gate(self, request=None):
        modem = self.modem or AtlantisModem()
        self.controller = modem.get_controller()
        self.controller.setup(request)
        self.controller.start()

    def get_state(self, request=None):
        if not self.is_available():
            return STATE_UNAVAILABLE
        elif request is None:
            return STATE_CLOSED
        elif request.is_ok():
            return STATE_OPEN
        elif request.is_pending():
            return STATE_RING
        else:
            return STATE_CLOSED


class HpccInternal(Gate):
    # RPi.GPIO viene importato dentro i metodi, non nell'__init__: così
    # istanziare HpccInternal non tocca l'hardware e la classe resta
    # importabile anche fuori dal Raspberry (dev, CI, migrations).
    def get_state(self, request=None):
        from hlcs.gpio import magnet_input

        return STATE_OPEN if magnet_input() else STATE_CLOSED

    def is_from_local_address(self, request):
        pattern = getattr(settings, "IP_PATTERN", r"^10\.87\.1\.\d{1,3}$")
        return re.match(pattern, request.address)

    def open_gate(self, request=None):
        if request is not None:
            if self.is_open():
                request.fail("Gate already open")
            elif not self.is_from_local_address(request):
                request.fail("Source is not local")
            elif request.user.is_staff:
                from hlcs.gpio import send_open_pulse

                send_open_pulse()
                self.state = STATE_OPEN
                request.done()
            else:
                request.fail("Access denied")
