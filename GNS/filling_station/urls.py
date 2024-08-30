from django.urls import path
from . import views, api
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from django.views.decorators.csrf import csrf_exempt


app_name = 'filling_station'

urlpatterns = [
    path('', views.balloons, name="balloons_list"),
    path('<str:nfc_tag>/', views.balloon_passport, name='balloon_passport'),
    path('reader/<str:reader>', views.reader_info, name="reader"),

    path('batch/balloons-loading', views.balloons_loading_batch, name="balloons_loading_batch"),
    path('batch/balloons-loading/<int:number>', views.balloons_loading_batch_details,
         name="balloons_loading_batch_details"),
    path('batch/balloons-unloading', views.balloons_unloading_batch, name="balloons_unloading_batch"),
    path('batch/balloons-unloading/<int:number>', views.balloons_unloading_batch_details,
         name="balloons_unloading_batch_details"),
    path('batch/railway-loading', views.railway_loading_batch, name="railway_loading_batch"),
    path('batch/railway-loading/<int:number>', views.railway_loading_batch_details, name="railway_loading_batch_details"),
    path('batch/auto-gas-loading', views.gas_loading_batch, name="auto_gas_loading_batch"),
    path('batch/auto-gas-loading/<int:number>', views.gas_loading_batch_details,
         name="auto_gas_loading_batch_details"),
    path('batch/auto-gas-unloading', views.gas_unloading_batch, name="auto_gas_unloading_batch"),
    path('batch/auto-gas-unloading/<int:number>', views.gas_unloading_batch_details,
         name="auto_gas_unloading_batch_details"),

    path('ttn', views.get_ttn, name="get_ttn"),
    path('ttn/<int:number>', views.get_ttn_details, name="get_ttn_details"),

    path('transport/trucks', views.get_trucks, name="trucks"),
    path('transport/trucks/<int:number>', views.get_trucks_details, name="trucks_details"),
    path('transport/trailers', views.get_trailers, name="trailers"),
    path('transport/trailers/<int:number>', views.get_trailers_details, name="trailers_details"),
    path('transport/railway', views.get_railway_tanks, name="railway_tanks"),
    path('transport/railway/<int:number>', views.get_railway_tanks_details, name="railway_tanks_details"),

    path('api/GetBalloonPassport', api.get_balloon_passport),
    path('api/UpdateBalloonPassport', api.update_balloon_passport),
    path('api/GetBalloonStateOptions', api.get_balloon_state_options),
    path('api/GetStationTrucks', api.get_station_trucks),

    path('api/StartLoading', csrf_exempt(api.start_loading)),
    path('api/StopLoading', api.stop_loading),
    path('api/StartUnloading', api.start_unloading),
    path('api/StopUnloading', api.stop_unloading),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # rfid readers main app
    path('api/rfid/GetBatchBalloons', api.get_batch_balloons),
    path('api/rfid/UpdateBatchBalloons', api.update_batch_balloons),
]
