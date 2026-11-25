from django.urls import path

from galeway.api.router import api

urlpatterns = [
    path("api/v1/", api.urls),
]
