from django.urls import path
from . import views, api
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)


app_name = 'filling_station'

urlpatterns = [
    path('', views.balloons, name="balloons_list"),
    path('reader/<str:reader>', views.reader_info, name="reader"),
    path('api/GetBalloonPassport', api.get_balloon_passport),
    path('api/UpdateBalloonPassport', api.update_balloon_passport),
    path('api/GetBalloonStateOptions', api.get_balloon_state_options),
    path('api/GetStationTrucks', api.get_station_trucks),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('client/', views.client, name="client"),
    # path('client/loading/', views.loading, name='loading'),
    # path('client/unloading/', views.unloading, name='unloading')
]
