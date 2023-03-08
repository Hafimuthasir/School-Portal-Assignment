from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Student
from .serializers import LoginSerializer
from school.jwt_utils import retrieve_id
from django.http import JsonResponse


class StudentLogin(APIView):
    """
    API view to authenticate a Student and generate a JWT Token.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                student = Student.objects.get(username=username)
            except Student.DoesNotExist:
                return Response({'message': 'Invalid username or password.', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

            if check_password(password, student.password):
                refresh = RefreshToken.for_user(student)

                access_token = str(refresh.access_token)

                response = JsonResponse(
                    {'message': 'Logged in successfully.', 'student_access_token': access_token, "status": "success"})
                response.set_cookie(key='student_access_token',
                                    value=access_token, httponly=True)

                return response

            else:
                return Response({'message': 'Invalid username or password.', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateInfo(APIView):
    """
    API view to update a student's name.
    """
    authentication_classes = []

    def put(self, request):
        if "student_access_token" in request.COOKIES:
            token = request.COOKIES.get("student_access_token")
            student_id = retrieve_id(token)
        else:
            return Response({'message': 'Login to make this request', 'status': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            student = Student.objects.get(id=student_id)

        except Student.DoesNotExist:
            return Response({'message': 'Student not found.', "status": "failed"}, status=status.HTTP_404_NOT_FOUND)

        name = request.data.get('name')
        new_password = request.data.get('new_password')
        old_password = request.data.get('old_password')

        if name and new_password:
            student.name = name
            if not old_password:
                return Response({'message': 'Old password is required', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            if check_password(old_password, student.password):
                student.password = make_password(new_password)
            else:
                return Response({'message': 'Incorrect Old password', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
            student.save()
            return Response({'message': 'Password and Name updated successfully.', 'status': "success"}, status=status.HTTP_200_OK)

        elif new_password and not name:
            if not old_password:
                return Response({'message': 'Old password is required', "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
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


class StudentLogout(APIView):
    """
    API view to Logout and remove the JWT Token from the client-side cookie.
    """

    def post(self, request):
        response = Response(
            {'message': 'Logged out successfully.', 'status': 'success'})

        # Delete the JWT cookie
        response.delete_cookie('student_access_token')

        return response
