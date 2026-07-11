from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from gatecontrol import views as gatecontrol_views
from hlcs import views as hlcs_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    re_path(
        r"^gates/(?P<gate_name>\w{0,50})/$",
        gatecontrol_views.gatecontrol,
        name="control",
    ),
    re_path(r"^gates/$", gatecontrol_views.get_all_states, name="gates"),
    re_path(
        r"^requests/(?P<gate_name>\w{0,50})/$",
        gatecontrol_views.show_requests,
        name="requests",
    ),
    path("about/", hlcs_views.about, name="about"),
    path("", hlcs_views.homepage, name="home"),
]
