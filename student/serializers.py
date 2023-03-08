from rest_framework import serializers
from .models import Student
from django.contrib.auth.hashers import make_password
from school.serializers import SchoolSerializer
from school.models import School

class StudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name =serializers.CharField(required=False)
    school = serializers.PrimaryKeyRelatedField(write_only=True, queryset=School.objects.all())


    class Meta:
        model = Student
        fields = ['name', 'username','grade', 'password','school' ]
        

    def create(self, validated_data):
        password = validated_data.pop('password')

        student = Student.objects.create(
            **validated_data,
            password=make_password(password)
        )

        return student
    
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

