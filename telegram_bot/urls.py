from django.urls import path, include
from .views import *

urlpatterns = [
    path('hook/', Hook.as_view()),
    path('setwebhook/', SetWebHook.as_view()),
]