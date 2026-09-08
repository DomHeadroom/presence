import re

from django.conf import settings
from django.shortcuts import render

from gatecontrol.views import get_client_ip

"""
Renders an HTML homepage
"""


def homepage(request):
    if not request.user.is_authenticated:
        return render(request, "index.html")
    gates = getattr(settings, "GATES", {})
    internal = gates["internal"]
    external = gates["external"]
    allowed = _internal_allowed(request)
    options = "" if allowed and not internal.is_open() else 'disabled="disabled"'
    external_options = "" if external.is_available() else 'disabled="disabled"'
    return render(
        request,
        "panel.html",
        {
            "options": options,
            "internal_allowed": allowed,
            "external_options": external_options,
        },
    )


def _internal_allowed(request):
    ip = get_client_ip(request)
    pattern = getattr(settings, "IP_PATTERN", r"^10\.87\.1\.\d{1,3}$")
    return bool(request.user.is_staff and ip and re.match(pattern, ip))


def about(request):
    return render(request, "about.html")
