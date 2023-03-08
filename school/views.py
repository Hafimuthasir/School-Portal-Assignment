from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import School
from student.models import Student
from .serializers import SchoolSerializer
from student.serializers import StudentSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from .jwt_utils import retrieve_id
from django.http import JsonResponse


# Create your views here.


class SchoolRegister(APIView):
    """
    API view to register a new School.
    """

    def post(self, request):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registered Successfully', 'status': 'success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolLogin(APIView):
    """
    API view to login a School and get JWT tokens.
    """

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            school = School.objects.get(email=email)
        except School.DoesNotExist:

            return Response({'message': 'Invalid email or password', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

        if not school.check_password(password):
            return Response({'message': 'Invalid email or password', "success": "failed"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(school)
        access_token = str(refresh.access_token)

        response = JsonResponse(
            {'message': 'Logged in successfully.', 'access_token': access_token, "status": "success"})
        response.set_cookie(key='access_token',
                            value=access_token, httponly=True)

        return response



class AddBulkStudents(APIView):
    """
    API view to bulk create students for a grade.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, grade):
        if "access_token" in request.COOKIES:
            token = request.COOKIES.get("access_token")
            schoolid = retrieve_id(token)
        else:
            return Response({'message': 'Login to make this request', 'status': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)

        if not schoolid:
            return Response({"message": "Authentication Error ", "status": "failed"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            school = School.objects.get(id=schoolid)

        except School.DoesNotExist:
            return Response({"message": "School does not exist", "status": "failed"}, status=status.HTTP_404_NOT_FOUND)

        students_data = request.data.get('students', [])

        saved_students = []
        errors = []

        for student_data in students_data:
            student_data['grade'] = grade
            student_data['school'] = schoolid

            serializer = StudentSerializer(data=student_data)
            if serializer.is_valid():
                student = serializer.save()
                saved_students.append(student)
            else:
                errors.append(
                    {"name": student_data['name'], "error": serializer.errors})

        error_count = len(errors)
        errored_students = []
        # for error in errors:
        #     print (error)
        #     errored_students.append({'name': error['name'][0]})

        if error_count == 0:
            return Response({"message": "All Data have been saved Successfully", "status": "success"})

        if len(saved_students) == 0:
            response_data = {
                'message': 'Failed to save the datas',
                'status': 'failed',
                'saved_students_count': len(saved_students),
                'saved_students': StudentSerializer(saved_students, many=True).data,
                'errored_students_count': error_count,
                'errored_students': errors
            }

        elif len(saved_students) >= 1:
            response_data = {
                'message': str(len(saved_students))+' datas saved successfully',
                'status': 'success',
                'saved_students_count': len(saved_students),
                'saved_students': StudentSerializer(saved_students, many=True).data,
                'errored_students_count': error_count,
                'errored_students': errors
            }

        return Response(response_data, status=status.HTTP_201_CREATED)


class FetchAll(APIView):
    """
    API view to fetch all students in the school.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if "access_token" in request.COOKIES:
            token = request.COOKIES.get("access_token")
            school_id = retrieve_id(token)
        else:
            return Response({'message': 'Login to make this request', 'status': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)

        school_obj = School.objects.get(id=school_id)
        students = Student.objects.filter(school=school_obj)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FilterByGrade(APIView):
    """
    API view to filter students based on grades.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, grade,):
        if "access_token" in request.COOKIES:
            token = request.COOKIES.get("access_token")
            school_id = retrieve_id(token)
        else:
            return Response({'message': 'Login to make this request', 'status': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)

        students = Student.objects.filter(grade=grade, school=school_id)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentCredentialsUpdate(APIView):
    """
    API view to update a student's name.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, student_id):
        if "access_token" in request.COOKIES:
            token = request.COOKIES.get("access_token")
            school_id = retrieve_id(token)
        else:
            return Response({'message': 'Login to make this request', 'status': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            school_obj = School.objects.get(id=school_id)

            student = Student.objects.get(id=student_id, school=school_obj)

        except Student.DoesNotExist:
            return Response({'message': 'Student not found in the school.', "status": "failed"}, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name')
        new_password = request.data.get('new_password')
        old_password = request.data.get('old_password')
        print(old_password)

        if name and new_password:
            student.name = name
            if not old_password:
                return Response({'message': 'Old password is required', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            if check_password(old_password, student.password):
                print('this is')
                student.password = make_password(new_password)
            else:
                print('did')
                return Response({'message': 'Incorrect Old password', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            student.save()
            return Response({'message': 'Password and Name updated successfully.', 'status': "success"}, status=status.HTTP_200_OK)

        elif new_password and not name:
            if not old_password:
                return Response({'message': 'Old password is required',  "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            if check_password(old_password, student.password):
                student.password = make_password(new_password)
            else:
                return Response({'message': 'Incorrect Old password', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            student.save()
            return Response({'message': 'Password updated successfully.', 'status': "success"}, status=status.HTTP_200_OK)

        elif name and not new_password:
            student.name = name
            student.save()
            return Response({'message': 'Name updated successfully.', 'status': "success"}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Name or Password field is required.', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class SchoolLogout(APIView):
    """
    API view to logout a School and remove the JWT access token cookie.
    """

    def post(self, request):
        response = JsonResponse(
            {'message': 'Logged out successfully.', "status": "success"})
        response.delete_cookie(key='access_token')
        return response
