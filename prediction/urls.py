from django.urls import path
from .views import predict_home_value

urlpatterns = [
    path('predict/', predict_home_value)
]
