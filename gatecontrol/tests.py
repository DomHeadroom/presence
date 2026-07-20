import time
from unittest.mock import MagicMock

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client, override_settings
from django.utils import timezone

from gatecontrol.gatecontrol import Gate, STATE_CLOSED
from gatecontrol.models import AccessRequest, REQUEST_STATE_OK
from gatecontrol.views import MAX_REQUESTS_LIMIT


class TestViews(TestCase):
    fixtures = ["users.json", "requests.json"]

    def parse_response(self, response):
        self.assertEqual(200, response.status_code)
        return response.json()

    def setUp(self):
        TestCase.setUp(self)
        mock = Gate()
        mock.get_state = MagicMock(return_value=STATE_CLOSED)
        mock.open_gate = MagicMock()
        setattr(settings, "GATES", {"test": mock})
        self.client = Client()
        self.assertTrue(self.client.login(username="admin", password="admin"))

    def test_get_all_states(self):
        expected = [{"test": STATE_CLOSED}]
        response = self.client.get(reverse("gates"))
        actual = self.parse_response(response)
        self.assertEqual(expected, actual)

    def test_gatecontrol(self):
        expected = {"req_id": 2}
        response = self.client.post(reverse("gate-open", args=("test",)))
        req_id = self.parse_response(response)
        self.assertEqual(expected, req_id)
        response = self.client.get(reverse("gate-state", args=("test",)), data=req_id)
        expected = {"description": "closed", "id": 0}
        actual = self.parse_response(response)
        self.assertEqual(expected.keys(), actual.keys())

    def test_show_requests(self):
        response = self.client.get(reverse("requests", args=("test",)))
        actual = self.parse_response(response)[0]
        expected = {"user": "admin", "time": "2015-03-01T17:28:18"}
        self.assertEqual(expected.keys(), actual.keys())

    def test_show_requests_invalid_limit(self):
        for bad in ("-1", "abc"):
            response = self.client.get(
                reverse("requests", args=("test",)), data={"limit": bad}
            )
            self.assertEqual(400, response.status_code)

    def test_show_requests_limit_capped(self):
        user = User.objects.get(username="admin")
        now = timezone.now()
        AccessRequest.objects.bulk_create(
            AccessRequest(
                user=user, req_time=now, req_state=REQUEST_STATE_OK, gate="test"
            )
            for _ in range(MAX_REQUESTS_LIMIT + 20)
        )
        response = self.client.get(
            reverse("requests", args=("test",)),
            data={"limit": MAX_REQUESTS_LIMIT + 50},
        )
        actual = self.parse_response(response)
        self.assertEqual(MAX_REQUESTS_LIMIT, len(actual))

    @override_settings(TRUSTED_PROXIES=["10.87.1.1"])
    def test_forwarded_for_ignores_spoofed_prefix(self):
        # client falso a sinistra, client reale (visto dal proxy) in mezzo,
        # proxy fidato in coda: deve vincere il reale, non il falso.
        self.client.post(
            reverse("gate-open", args=("test",)),
            HTTP_X_FORWARDED_FOR="10.87.1.5, 203.0.113.9, 10.87.1.1",
        )
        r = AccessRequest.objects.filter(gate="test").order_by("-id").first()
        self.assertEqual("203.0.113.9", r.address)

    @override_settings(TRUSTED_PROXIES=["10.87.1.1"])
    def test_forwarded_for_onsite(self):
        self.client.post(
            reverse("gate-open", args=("test",)),
            HTTP_X_FORWARDED_FOR="10.87.1.130, 10.87.1.1",
        )
        r = AccessRequest.objects.filter(gate="test").order_by("-id").first()
        self.assertEqual("10.87.1.130", r.address)


class TestManager(TestCase):
    fixtures = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_get_pending_request(self):
        r1 = AccessRequest.objects.request_access(self.user, "127.0.0.1", MagicMock(), "test")
        self.assertEqual(r1, AccessRequest.objects.get_pending_request("test"))

    def test_get_last_accesses(self):
        u = self.user
        r1 = AccessRequest.objects.request_access(u, "127.0.0.1", Gate(), "test")
        r1.done()
        time.sleep(1)
        r2 = AccessRequest.objects.request_access(u, "127.0.0.1", Gate(), "test")
        r2.done()
        accesses = [a.id for a in AccessRequest.objects.get_last_accesses("test")]
        self.assertEqual([r2.id, r1.id], accesses)
