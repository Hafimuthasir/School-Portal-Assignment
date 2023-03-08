from django.urls import path
from .views import *

urlpatterns = [
    path('register', SchoolRegister.as_view(), name="register_school"),
    path('login', SchoolLogin.as_view(), name="login_school"),
    path('add_students/<grade>', AddBulkStudents.as_view(), name="add_bulk"),
    path('fetch_students', FetchAll.as_view(), name='fetch_all'),
    path('filter_by_grade/<grade>', FilterByGrade.as_view(), name='filterbygrade'),
    path('update_student_info/<student_id>', StudentCredentialsUpdate.as_view(), name='update_std_name'), 
    path('logout', SchoolLogout.as_view(), name="logout")
]
