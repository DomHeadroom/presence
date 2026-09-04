from unittest.mock import MagicMock, Mock

from django.test import TestCase
from serial import Serial
from serial.serialutil import SerialException

from hlcs import modem
from hlcs.gates import HpccInternal
from hlcs.modem import AtlantisModem


class TestLocalAddress(TestCase):
    def _is_local(self, address):
        return HpccInternal().is_from_local_address(Mock(address=address))

    def test_lan_ip_is_local(self):
        self.assertTrue(self._is_local("10.87.1.130"))

    def test_public_ip_not_local(self):
        self.assertFalse(self._is_local("203.0.113.9"))

    def test_escaped_dots(self):
        # con i punti non escapati questa stringa passerebbe come "locale"
        self.assertFalse(self._is_local("10X87X1X5"))

    def test_no_trailing_garbage(self):
        # l'ancora finale impedisce che una coda spuria venga accettata
        self.assertFalse(self._is_local("10.87.1.5.evil.com"))


class TestAtlantisModemController(TestCase):
    def testDone(self):
        request = Mock()
        serial = Mock()
        serial.readline = MagicMock(return_value=modem.MSG_OK)
        controller = modem.AtlantisModemController(serial)
        controller.setup(request)
        serial.read = MagicMock(return_value=modem.MSG_RING)
        serial.readline = MagicMock(return_value=modem.MSG_BUSY)
        controller.run()
        request.done.assert_called_with()

    def testFail(self):
        request = Mock()

        try:
            serial = Serial(AtlantisModem.PORT, baudrate=AtlantisModem.BAUDRATE)
        except SerialException:
            serial = Mock()
            serial.readline = MagicMock(return_value=modem.MSG_OK)
            serial.read = MagicMock(return_value=None)

        controller = modem.AtlantisModemController(serial)
        controller.setup(request)
        controller.run()
        request.fail.assert_called_with("no RING received")
