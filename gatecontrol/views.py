from django.conf import settings
from django.http.response import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from gatecontrol.models import AccessRequest

# tetto per ?limit di show_requests: l'endpoint e' anonimo, niente query a
# taglia decisa dal client
MAX_REQUESTS_LIMIT = 20


def get_client_ip(request):
    """IP reale del client dall'header X-Forwarded-For.

    L'XFF e' una catena ``client, proxy1, proxy2, ...``: il client vero sta a
    sinistra, ogni reverse proxy si aggiunge a destra. Prendere il primo
    elemento (``xff.split(',')[0]``, come fanno gli snippet in giro) e'
    spoofabile perche' quella posizione la imposta chi manda la richiesta;
    prendere l'ultimo darebbe il proxy. Quindi togliamo dalla catena i proxy
    noti (``settings.TRUSTED_PROXIES``) e teniamo l'ultimo IP rimasto: e' il
    primo, partendo da destra, che non e' un nostro proxy. Se non resta nulla
    (catena vuota, o tutta di proxy nostri) usiamo REMOTE_ADDR, che non e'
    falsificabile a livello applicativo.
    """
    trusted = set(getattr(settings, "TRUSTED_PROXIES", []))
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    hops = [ip.strip() for ip in xff.split(",") if ip.strip()]
    client_hops = [ip for ip in hops if ip not in trusted]
    return client_hops[-1] if client_hops else request.META.get("REMOTE_ADDR")


### JSON API ###
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_states(request):
    gates = getattr(settings, "GATES", {})
    response = [{g: gates[g].get_state()} for g in gates]
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
    address = get_client_ip(request) or "unknown"
    r = AccessRequest.objects.request_access(
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
    if limit < 0:
        return HttpResponseBadRequest()
    access_requests = AccessRequest.objects.get_last_accesses(
        gate_name, min(limit, MAX_REQUESTS_LIMIT)
    )
    response = [
        {
            "time": r.req_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "user": r.user.username,
        }
        for r in access_requests
    ]
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
