from rest_framework import serializers
from .models import School
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from student.models import Student

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['email', 'name', 'city', 'pin_code','password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value
    

    def validate_email(self, value):
        validate_email(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields=['name','username','grade']