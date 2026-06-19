from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_view, name='root'),

    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Student Management URLs
    path('student-list/', views.student_list, name='student_list'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('student/<int:student_id>/password/', views.change_student_password, name='change_student_password'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),

    # Staff Management URLs
    path('staff-list/', views.staff_list, name='staff_list'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('edit-staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('staff/<int:staff_id>/password/', views.change_staff_password, name='change_staff_password'),

    # Schedule URLs
    path('day-schedule/', views.day_schedule, name='day_schedule'),
    path('day-schedule/<int:schedule_id>/delete/', views.delete_day_schedule, name='delete_day_schedule'),
    
    # Attendance URLs
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('edit-attendance/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance-adjustment/', views.add_attendance_adjustment, name='add_attendance_adjustment'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
    path('attendance-percentage/', views.attendance_percentage, name='attendance_percentage'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
]
