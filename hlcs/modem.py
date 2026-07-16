"""
Copyright (C) 2014, Vincenzo Pirrone <pirrone.v@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import threading

import serial
import logging
import time


logger = logging.getLogger(__name__)

# constants
MSG_OK = b"OK\r\n"
MSG_RING = b"\r\nRING\r\n"
MSG_BUSY = b"BUSY\r\n"
MSG_OPEN = b"atdt*\r"

INIT_COMMANDS = (b"at\r", b"atz\r", b"at*nc9\r", b"atx3\r", b"ats11=60\r", b"ats0=0\r")

ECHO_WAIT = 1
INIT_CMD_WAIT = 5


class Modem:
    def get_controller(self):
        pass


class ModemController:
    def setup(self, request):
        self.request = request


class DummyModem(Modem):
    def get_controller(self):
        return DummyController()


class DummyController(threading.Thread, ModemController):
    WAIT = 10

    def run(self):
        threading.Thread.run(self)
        time.sleep(DummyController.WAIT)
        self.request.done()


class AtlantisModem(Modem):
    PORT = "/dev/ttyUSB0"
    BAUDRATE = 115200

    def __init__(self):
        self._check_connection()

    def _get_serial(self):
        return serial.Serial(AtlantisModem.PORT, baudrate=AtlantisModem.BAUDRATE)

    def _check_connection(self):
        try:
            s = self._get_serial()
            s.close()
        except Exception as e:
            print(f"ERROR: {__name__}: {str(e)}")
            sys.exit(1)

    def get_controller(self):
        logger.debug("opening serial port..")
        ser = self._get_serial()
        logger.debug("serial port opened")
        return AtlantisModemController(ser)


class AtlantisModemController(threading.Thread, ModemController):
    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial = serial

    def setup(self, request, timeout=60):

        self.request = request

        try:
            self.serial.timeout = INIT_CMD_WAIT

            logger.debug("flushing buffers")
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            logger.debug("sending init commands to modem..")
            for c in INIT_COMMANDS:
                logger.debug(f"sending {c}")
                self.serial.write(c)
                logger.debug("reading echo")
                echo = self.serial.readline()  # echo
                if len(echo) == 0:
                    raise IOError("no echo received")
                else:
                    ok = self.serial.readline()
                    if ok != MSG_OK:
                        raise IOError(f"error at comand: {c}")

            self.serial.timeout = timeout
            logger.debug("setup complete, controller in listen mode")

        except Exception as e:
            try:
                self.serial.close()
            except Exception:
                pass
            logger.exception(e)
            self.request.fail(str(e))

    def run(self):
        try:
            logger.debug("modem in listen mode")

            lineIn = self.serial.read(len(MSG_RING))
            if lineIn == MSG_RING:
                logger.debug("RING received")
                logger.debug("sending *")
                self.serial.write(MSG_OPEN)
                while lineIn != MSG_BUSY and len(lineIn) > 0:
                    lineIn = self.serial.readline()
                    logger.debug(f"modem: {lineIn.rstrip()}")
                if lineIn == MSG_BUSY:
                    logger.info("door opened")
                    self.request.done()
                else:
                    msg = f"invalid input: {lineIn.rstrip()}"
                    logger.error(msg)
                    self.request.info = msg
            else:
                msg = "no RING received"
                logger.debug(msg)
                self.request.fail(msg)

            logger.debug("closing serial port")
            self.serial.close()
        except Exception as e:
            logger.exception(e)
            self.request.fail(str(e))
