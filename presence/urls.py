from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from gatecontrol import views as gatecontrol_views
from hlcs import views as hlcs_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("gates/<str:gate_name>/", gatecontrol_views.gatecontrol_get, name="gate-state"),
    path("gates/<str:gate_name>/open/", gatecontrol_views.gatecontrol_post, name="gate-open"),
    path("gates/", gatecontrol_views.get_all_states, name="gates"),
    path("requests/<str:gate_name>/", gatecontrol_views.show_requests, name="requests"),
    path("about/", hlcs_views.about, name="about"),
    path("", hlcs_views.homepage, name="home"),
]
