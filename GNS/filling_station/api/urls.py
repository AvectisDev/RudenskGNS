from django.urls import path
from . import api
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from django.views.decorators.csrf import csrf_exempt


app_name = 'filling_station'

urlpatterns = [
    path('BalloonPassport', api.BalloonView.as_view()),
    path('GetBalloonStateOptions', api.get_balloon_state_options),

    path('GetTrucks', api.TruckView.as_view()),
    path('GetTrailers', api.TrailerView.as_view()),

    path('BalloonsLoading', api.BalloonsLoadingBatchView.as_view()),
    path('BalloonsUnloading', api.BalloonsUnloadingBatchView.as_view()),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
