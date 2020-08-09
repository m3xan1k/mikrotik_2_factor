from django.urls import path
from clients.views import ConnectView, ConfirmView, DisconnectView, TimeCheckView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('connect/', csrf_exempt(ConnectView.as_view()), name=ConnectView.name),
    path('disconnect/', csrf_exempt(DisconnectView.as_view()), name=DisconnectView.name),
    path('confirm/', csrf_exempt(ConfirmView.as_view()), name=ConfirmView.name),
    path('timecheck/', TimeCheckView.as_view(), name=TimeCheckView.name),
]
