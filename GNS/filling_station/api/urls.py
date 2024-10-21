from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from django.views.decorators.csrf import csrf_exempt


app_name = 'filling_station'


balloons_loading_router = DefaultRouter()
balloons_loading_router.register(r'balloons-loading',
                                 api.BalloonsLoadingBatchViewSet,
                                 basename='balloons-loading')

balloons_unloading_router = DefaultRouter()
balloons_unloading_router.register(r'balloons-unloading',
                                   api.BalloonsUnloadingBatchViewSet,
                                   basename='balloons-unloading')

urlpatterns = [
    path('balloon-passport', api.BalloonView.as_view()),
    path('balloon-status-options', api.get_balloon_status_options),
    path('loading-balloon-reader-list', api.get_loading_balloon_reader_list),
    path('unloading-balloon-reader-list', api.get_unloading_balloon_reader_list),

    path('trucks', api.TruckView.as_view()),
    path('trailers', api.TrailerView.as_view()),
    path('railway-tanks', api.RailwayTanksView.as_view()),

    path('', include(balloons_loading_router.urls)),
    path('', include(balloons_unloading_router.urls)),

    path('railway-loading', api.RailwayBatchView.as_view()),
    path('auto-gas', api.AutoGasBatchView.as_view()),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
