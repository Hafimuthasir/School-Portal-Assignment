from django.contrib import admin
from .models import School
from student.models import Student
from django.contrib.auth.models import Group

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'grade')
    list_filter = ('grade','school')


    def filter_students(self, request, queryset):
        school_id = request.POST.get('school_id')
        grade = request.POST.get('grade')

        if school_id and grade:
            queryset = queryset.filter(school_id=school_id, grade=grade)

        return queryset

    filter_students.short_description = 'Filter students by school and grade'



class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name','email','city','pin_code')

admin.site.register(Student, StudentAdmin)
admin.site.register(School, SchoolAdmin)
# admin.site.unregister(User)
admin.site.unregister(Group)