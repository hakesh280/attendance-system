from django.contrib import admin
from .models import (
    Student, Staff, Subject, Period, Attendance, AttendanceAdjustment,
    Notification, StaffSubjectAssignment, DaySchedule
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'department', 'semester', 'user')
    list_filter = ('department', 'semester')
    search_fields = ('name', 'roll_number')
    ordering = ('roll_number',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'designation', 'user')
    list_filter = ('department', 'designation')
    search_fields = ('name', 'department')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name', 'subject_code', 'semester')
    list_filter = ('semester',)
    search_fields = ('subject_name', 'subject_code')


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('period_code', 'start_time', 'end_time')
    ordering = ('period_code',)


@admin.register(StaffSubjectAssignment)
class StaffSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('staff', 'subject', 'department', 'semester')
    list_filter = ('department', 'semester', 'subject')
    search_fields = ('staff__name', 'subject__subject_name', 'department')


@admin.register(DaySchedule)
class DayScheduleAdmin(admin.ModelAdmin):
    list_display = ('date', 'department', 'semester', 'period', 'subject', 'staff')
    list_filter = ('date', 'department', 'semester', 'period')
    search_fields = ('department', 'subject__subject_name', 'staff__name')
    date_hierarchy = 'date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'period', 'status', 'staff', 'changed_by')
    list_filter = ('date', 'period', 'status', 'subject')
    search_fields = ('student__name', 'subject__subject_name')
    date_hierarchy = 'date'
    ordering = ('-date', '-period')


@admin.register(AttendanceAdjustment)
class AttendanceAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance_count', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__name', 'student__roll_number', 'opinion')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
