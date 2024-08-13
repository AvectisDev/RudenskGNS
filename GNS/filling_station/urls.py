from django.urls import path
from . import views, api
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)


urlpatterns = [
    # path('', views.index, name="home"),
    path('reader/<str:reader>', views.reader_info, name="ballons_table"),
    path('api/getBalloonPassport', api.get_balloon_passport, name="ballons_table"),
    path('api/UpdateBalloonPassport', api.update_balloon_passport, name="ballons_table"),
    path('api/UpdateBalloonStateOptions', api.get_balloon_state_options, name="ballons_table"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('client/', views.client, name="client"),
    # path('client/loading/', views.loading, name='loading'),
    # path('client/unloading/', views.unloading, name='unloading')
]
