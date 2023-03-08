from django.urls import path
from .views import *

urlpatterns = [
    path('login', StudentLogin.as_view(), name="login_student"),
    path('update_info', UpdateInfo.as_view(), name="credentials_update"),
    path('logout', StudentLogout.as_view(), name="credentials_update")
]
