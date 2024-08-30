from django.urls import path
from . import api
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from django.views.decorators.csrf import csrf_exempt


app_name = 'filling_station'

urlpatterns = [
    path('BalloonPassport/<str:nfc_tag>/', api.BalloonView.as_view()),
    path('GetBalloonStateOptions', api.get_balloon_state_options),
    path('GetStationTrucks', api.get_station_trucks),

    path('StartLoading', csrf_exempt(api.start_loading)),
    path('StopLoading', api.stop_loading),
    path('StartUnloading', api.start_unloading),
    path('StopUnloading', api.stop_unloading),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # rfid readers main app
    path('rfid/GetBatchBalloons', api.get_batch_balloons),
    path('rfid/UpdateBatchBalloons', api.update_batch_balloons),
]
