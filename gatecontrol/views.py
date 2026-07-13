from django.conf import settings
from django.http.response import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from gatecontrol.models import AccessRequest


### JSON API ###
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_states(request):
    gates = getattr(settings, "GATES", {})
    response = []
    for g in gates.keys():
        response.append({g: gates[g].get_state()})
    return JsonResponse(response, safe=False)


@api_view(["GET"])
@permission_classes([AllowAny])
def gatecontrol_get(request, gate_name):
    gates = getattr(settings, "GATES")
    if gates is None or gate_name not in gates:
        raise Http404
    gate = gates[gate_name]
    return _get_state(gate, request.GET.get("req_id", None))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gatecontrol_post(request, gate_name):
    gates = getattr(settings, "GATES")
    if gates is None or gate_name not in gates:
        raise Http404
    gate = gates[gate_name]
    # TODO: DA TESTARE
    address = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR", "unknown")
    r = AccessRequest.objects.get_or_create(
        request.user, address, gate, gate_name
    )
    return JsonResponse({"req_id": r.id})


@api_view(["GET"])
@permission_classes([AllowAny])
def show_requests(request, gate_name):
    gates = getattr(settings, "GATES")
    if gates is None or gate_name not in gates:
        raise Http404
    try:
        limit = int(request.GET.get("limit", "10"))
    except ValueError:
        return HttpResponseBadRequest()
    access_requests = AccessRequest.objects.get_last_accesses(gate_name, limit)
    response = []
    for r in access_requests:
        response.append(
            {"time": r.req_time.strftime("%Y-%m-%dT%H:%M:%S"), "user": r.user.username}
        )
    return JsonResponse(response, safe=False)


def _get_state(gate, access_request_id):
    if access_request_id is not None:
        try:
            req_id = int(access_request_id)
        except ValueError:
            return HttpResponseBadRequest()
        r = get_object_or_404(AccessRequest, pk=req_id)
    else:
        r = None
    state = gate.get_state(r)
    return JsonResponse(state)
